from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Any, Callable, Optional, Protocol

from app.domain.exceptions.domain_exception import TimelineConflictException, NotFoundException


class TimelineEventProtocol(Protocol):
    """
    Protocol ensuring objects passed to the calculator have the necessary fields.
    """
    id: Optional[int]
    start_time: datetime
    end_time: Optional[datetime]


@dataclass
class TimelineChangePlan:
    to_create: List[Any] = None
    to_update: List[Any] = None
    to_delete_ids: List[int] = None

    def __post_init__(self):
        self.to_create = self.to_create or []
        self.to_update = self.to_update or []
        self.to_delete_ids = self.to_delete_ids or []


class TimelineCalculator:
    def calculate_changes(
            self,
            current_events: List[Any],
            updates: List[Any],
            creates: List[Any] = None,  # Explicit creates list
            deletes: List[int] = None,  # Explicit deletes list
            auto_fix: bool = False,
            model_factory: Callable[[Any], Any] = None,  # Factory function
    ) -> TimelineChangePlan:

        creates = creates or []
        deletes = deletes or []
        plan = TimelineChangePlan(to_delete_ids=deletes)

        # 1. Filter out deleted events from current timeline view
        # Optimization: Use set for O(1) lookup
        deletes_set = set(deletes)
        timeline = [e for e in current_events if getattr(e, 'id', None) not in deletes_set]

        # Optimization: Map ID to event for O(1) update lookup
        # Only map events that have an ID (existing events)
        timeline_map = {e.id: e for e in timeline if getattr(e, 'id', None) is not None}

        # 2. Apply Updates
        for update in updates:
            # Find event in timeline map (O(1) lookup)
            target = timeline_map.get(update.id)

            if not target:
                raise NotFoundException(f"Event {update.id} not found or marked for deletion")

            # Apply fields
            # Safer check for Pydantic models vs Dicts
            if hasattr(update, "model_dump"):
                data = update.model_dump(exclude_unset=True, exclude={'id'})
            else:
                data = getattr(update, "__dict__", {})

            for k, v in data.items():
                if hasattr(target, k):
                    setattr(target, k, v)

            if target not in plan.to_update:
                plan.to_update.append(target)

        # 3. Apply Creates
        if creates:
            if not model_factory:
                raise ValueError("Model factory required for creating new events")

            for create_schema in creates:
                new_event = model_factory(create_schema)
                plan.to_create.append(new_event)
                timeline.append(new_event)

        # 4. Sort
        # We sort by start_time, and then by end_time (handling None as infinity).
        def sort_key(x):
            start_t = x.start_time
            end_val = x.end_time

            if end_val is None:
                # Handle timezone aware comparisons
                if start_t.tzinfo:
                    end_val = datetime.max.replace(tzinfo=timezone.utc)
                else:
                    end_val = datetime.max
            return start_t, end_val

        timeline.sort(key=sort_key)

        # 5. Sweep Line (Overlap Check)
        for i in range(len(timeline) - 1):
            previous_event = timeline[i]
            next_event = timeline[i + 1]

            current_end = previous_event.end_time
            next_start = next_event.start_time

            has_overlap = False
            if current_end is None:
                has_overlap = True
            elif current_end > next_start:
                has_overlap = True

            if has_overlap:
                if not auto_fix:
                    c_id = getattr(previous_event, 'id', 'New')
                    n_id = getattr(next_event, 'id', 'New')
                    raise TimelineConflictException(
                        f"Overlap detected: Event {c_id} overlaps Event {n_id}",
                        conflicting_events=[
                            {"id": c_id, "end": current_end},
                            {"id": n_id, "start": next_start}
                        ]
                    )

                # Auto Fix: Truncate previous event
                previous_event.end_time = next_start

                # EDGE CASE: Zero Duration
                # If truncating makes start == end, the event effectively disappears.
                if previous_event.start_time == previous_event.end_time:
                    # Remove from update/create lists if present
                    if previous_event in plan.to_update:
                        plan.to_update.remove(previous_event)
                    if previous_event in plan.to_create:
                        plan.to_create.remove(previous_event)

                    # If it's an existing DB event, we must delete it
                    c_id = getattr(previous_event, 'id', None)
                    if c_id and c_id not in plan.to_delete_ids:
                        plan.to_delete_ids.append(c_id)
                else:
                    # Normal update
                    if previous_event not in plan.to_update and previous_event not in plan.to_create:
                        plan.to_update.append(previous_event)

        return plan
