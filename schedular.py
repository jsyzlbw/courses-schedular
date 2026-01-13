from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple


# ----------------------------
# Core schedule representation
# ----------------------------

# Convert the day of the week to number
DAY_ORDER = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}


def _to_minutes(t: str) -> int:
    """
    Convert a time string like '8:30' or '13:30' into minutes since midnight.
    Assumes 24-hour time if >= 12 and no AM/PM suffix is provided.
    """
    t = t.strip()
    # If you later decide to support "8:30 AM" / "8:30PM", you can extend here.
    hours, minutes = t.split(":")
    return int(hours) * 60 + int(minutes)


@dataclass(frozen = True)
class Meeting:
    """
    Meeting is a data type, and use a triplet to store day, start_min, end_min
    Meeting(day, start_min, end_min)
    """
    day: str
    start_min: int
    end_min: int
    

    @staticmethod
    def from_triplet(day: str, start: str, end: str) -> "Meeting":
        return Meeting(day = day, start_min = _to_minutes(start), end_min = _to_minutes(end))

    def overlaps(self, other: "Meeting") -> bool:
        """Time-interval overlap on the same day."""
        if self.day != other.day:
            return False
        # Overlap if intervals intersect: [s1, e1] and [s2, e2]
        return self.start_min < other.end_min and other.start_min < self.end_min


@dataclass(frozen=True)
class Section:
    course_code: str
    professor: str
    meetings: Tuple[Meeting, ...] # meetings store all the sections

    @staticmethod
    def from_raw(course_code: str, raw_section: List[Any]) -> "Section":
        """
        raw_section format:
            ["Prof Name", ["Mon","8:30","10:20"], ["Wed","13:30","14:50"], ...]
        """
        professor = raw_section[0]
        meetings: List[Meeting] = []
        for triplet in raw_section[1:]:
            day, start, end = triplet
            meetings.append(Meeting.from_triplet(day, start, end))
        return Section(course_code = course_code, professor = professor, meetings = tuple(meetings))


def _starts_at_830(meeting: Meeting) -> bool:
    return meeting.start_min == _to_minutes("8:30")


def _is_friday(meeting: Meeting) -> bool:
    return meeting.day == "Fri"


def _normalize_day(day: str) -> str:
    # Basic normalization; extend if your data uses variants like "Monday", "MON", etc.
    day = day.strip()
    # Common variants (optional)
    mapping = {
        "Monday": "Mon",
        "Tuesday": "Tue",
        "Wednesday": "Wed",
        "Thursday": "Thu",
        "Friday": "Fri",
        "Saturday": "Sat",
        "Sunday": "Sun",
    }
    return mapping.get(day, day)


# ----------------------------
# Public function
# ----------------------------

def find_non_conflicting_schedules(
    course_data: Dict[str, List[List[Any]]],
    course_choice: Dict[str, str],
    morning_eight_avoid: bool = False,
    friday_avoid: bool = False,
) -> List[Dict[str, Any]]:
    """
    Args:
        course_data:
            {course_code: [section_list]}
            section_list element:
                ["Prof Name", ["Mon","8:30","10:20"], ["Wed","13:30","14:50"], ...]
        course_choice:
            {course_code: professor_name OR "prof" (meaning any professor acceptable)}
        morning_eight_avoid:
            If True, exclude any section that has a meeting starting at 8:30.
        friday_avoid:
            If True, exclude any section that has any meeting on Friday.

    Returns:
        A list of feasible schedules. Each schedule is a dict:
            {
              "sections": {
                  "CSC1001": {"professor": "...", "meetings": [("Mon","8:30","10:20"), ...]},
                  ...
              },
              "compact": [("Mon","8:30","10:20","CSC1001","Tom Anderson"), ...]  # sorted
            }
        If no feasible schedule exists, returns [].
    """
    # 1) Build candidate sections per requested course, applying professor and avoidance filters.
    candidates: Dict[str, List[Section]] = {}

    for course_code, prof_wanted in course_choice.items():
        raw_sections = course_data.get(course_code, [])
        section_objs: List[Section] = []

        for raw in raw_sections:
            sec = Section.from_raw(course_code, raw)

            # Normalize day names inside the section (optional but safe)
            normalized_meetings = tuple(
                Meeting(_normalize_day(m.day), m.start_min, m.end_min) for m in sec.meetings
            )
            sec = Section(course_code=sec.course_code, professor=sec.professor, meetings=normalized_meetings)

            # Professor filter
            if prof_wanted != "prof" and sec.professor != prof_wanted:
                continue

            # Morning 8:30 avoidance
            if morning_eight_avoid and any(_starts_at_830(m) for m in sec.meetings):
                continue

            # Friday avoidance
            if friday_avoid and any(_is_friday(m) for m in sec.meetings):
                continue

            section_objs.append(sec)

        # If any requested course has zero viable sections, there is no solution.
        if not section_objs:
            return []

        candidates[course_code] = section_objs

    # 2) Backtracking search with pruning for conflicts.
    course_list = sorted(candidates.keys())  # deterministic ordering
    results: List[Dict[str, Any]] = []

    chosen: Dict[str, Section] = {}
    occupied: List[Meeting] = []  # meetings already placed

    def conflicts_with_occupied(sec: Section) -> bool:
        for m in sec.meetings:
            for o in occupied:
                if m.overlaps(o):
                    return True
        return False

    def backtrack(i: int) -> None:
        if i == len(course_list):
            # Build a user-friendly schedule record
            schedule = {"sections": {}, "compact": []}
            compact_rows: List[Tuple[str, str, str, str, str]] = []

            for c in course_list:
                sec = chosen[c]
                mtgs_readable = []
                for m in sec.meetings:
                    start = f"{m.start_min // 60}:{m.start_min % 60:02d}"
                    end = f"{m.end_min // 60}:{m.end_min % 60:02d}"
                    mtgs_readable.append((m.day, start, end))
                    compact_rows.append((m.day, start, end, c, sec.professor))

                schedule["sections"][c] = {
                    "professor": sec.professor,
                    "meetings": mtgs_readable,
                }

            compact_rows.sort(key=lambda r: (DAY_ORDER.get(r[0], 99), _to_minutes(r[1])))
            schedule["compact"] = compact_rows
            results.append(schedule)
            return

        course_code = course_list[i]
        for sec in candidates[course_code]:
            if conflicts_with_occupied(sec):
                continue
            chosen[course_code] = sec
            occupied.extend(sec.meetings)
            backtrack(i + 1)
            # undo
            for _ in range(len(sec.meetings)):
                occupied.pop()
            chosen.pop(course_code, None)

    backtrack(0)
    return results


# ----------------------------
# Example usage (your sample)
# ----------------------------
if __name__ == "__main__":
    course_data = {
        "CSC1001": [
            ["Tom Anderson", ["Mon", "8:30", "10:20"], ["Wed", "13:30", "14:50"]],
            ["Judy Trump", ["Tue", "8:30", "10:20"], ["Thu", "13:30", "14:50"]],
        ],
        "MAT1011": [
            ["Joe Tompson", ["Mon", "10:30", "11:50"], ["Wed", "10:30", "11:50"], ["Thu", "10:30", "12:20"]],
        ],
    }

    course_choice = {
        "CSC1001": "prof",
        "MAT1011": "Joe Tompson",
    }

    schedules = find_non_conflicting_schedules(
        course_data,
        course_choice,
        morning_eight_avoid=False,
        friday_avoid=False,
    )

    print(f"Found {len(schedules)} schedule(s).")
    for idx, s in enumerate(schedules, 1):
        print(f"\nSchedule #{idx}")
        for row in s["compact"]:
            day, start, end, code, prof = row
            print(f"  {day} {start}-{end}  {code}  ({prof})")
