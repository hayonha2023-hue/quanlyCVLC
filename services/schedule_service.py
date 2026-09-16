import copy
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import logging
from zoneinfo import ZoneInfo
app_logger = logging.getLogger(__name__)


class ScheduleService:
    """Tách biệt thuật toán xếp lịch khỏi giao diện."""

    SPECIAL_MAX_DAYS_PER_WEEK = 2

    @staticmethod
    def _special_day_plan(excluded_names: List[str]) -> Dict[str, set[int]]:
        """Chọn ngẫu nhiên thực sự các ngày được phép xếp cho NV đặc biệt.

        - Mỗi NV đặc biệt tối đa 2 ngày/tuần.
        - Ưu tiên 2 ngày không liền nhau để không xung đột với luật chống trực liên tiếp.
        - Mỗi lần bấm SẮP LỊCH sẽ tạo kế hoạch mới bằng SystemRandom, nên không còn
          mẫu cố định Thứ 2 -> Thứ 4 do vòng lặp đi từ đầu tuần.
        """
        rng = random.SystemRandom()
        # Các cặp không liền nhau trong cùng tuần.
        pairs = [(a, b) for a in range(7) for b in range(a + 1, 7) if abs(a - b) > 1]
        result: Dict[str, set[int]] = {}
        for raw_name in excluded_names:
            name = str(raw_name or "").strip().lower()
            if not name:
                continue
            if pairs:
                result[name] = set(rng.choice(pairs))
            else:
                result[name] = set(rng.sample(range(7), k=min(2, 7)))
        return result

    @staticmethod
    def generate_weekly_schedule(
        pools: Dict[str, List[str]],
        excluded_names: List[str],
        current_stats: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Sắp lịch tuần tiếp theo theo công bằng + random ngày cho NV đặc biệt."""
        try:
            td = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
            # Thứ Hai của tuần kế tiếp.
            st_d = (td + timedelta(days=(7 - td.weekday()))).replace(
                hour=0, minute=0, second=0, microsecond=0
            )

            nw: Dict[str, Any] = {}
            daily_all_staff: List[List[str]] = []

            active_shifts = [ca for ca in ["Sáng", "Chiều", "10h30"] if ca in pools]
            new_stats = {
                k: v.copy() if isinstance(v, dict) else v
                for k, v in current_stats.items()
            }

            excluded_lower = {
                str(n or "").strip().lower()
                for n in excluded_names
                if str(n or "").strip()
            }
            special_days = ScheduleService._special_day_plan(list(excluded_lower))

            for day_index in range(7):
                day = st_d + timedelta(days=day_index)
                ds = day.strftime("%d/%m - %A")
                tds = {ca: [] for ca in active_shifts}
                today_all: List[str] = []

                for ca in active_shifts:
                    pool = pools.get(ca, [])
                    valid_staff = [n for n in pool if n not in today_all]

                    # NV đặc biệt chỉ được tham gia pool ở đúng các ngày random đã chọn.
                    filtered: List[str] = []
                    for n in valid_staff:
                        nl = n.strip().lower()
                        if nl in excluded_lower:
                            if day_index in special_days.get(nl, set()):
                                filtered.append(n)
                        else:
                            filtered.append(n)

                    # Nếu lọc đặc biệt làm pool quá nhỏ, vẫn giữ các NV thường;
                    # tuyệt đối không ép NV đặc biệt vào ngày không được random.
                    valid_staff = filtered

                    scored = []
                    for n in valid_staff:
                        consecutive_penalty = (
                            1000
                            if daily_all_staff and n in daily_all_staff[-1]
                            else 0
                        )
                        week_count = sum(
                            1
                            for prev_d in nw.values()
                            for shift_names in prev_d.values()
                            if n in shift_names
                        )

                        stat = new_stats.get(n, {})
                        if isinstance(stat, dict):
                            previous_total = stat.get("ca", 0)
                            previous_shift = stat.get(ca, 0)
                        else:
                            previous_total = stat if isinstance(stat, (int, float)) else 0
                            previous_shift = 0

                        # random_tie là khóa cuối cùng: chỉ phá hòa, không phá công bằng.
                        scored.append({
                            "n": n,
                            "consec": consecutive_penalty,
                            "cw": week_count,
                            "pc_spec": previous_shift,
                            "pc_tot": previous_total,
                            "random_tie": random.SystemRandom().random(),
                        })

                    scored.sort(
                        key=lambda x: (
                            x["consec"],
                            x["cw"],
                            x["pc_spec"],
                            x["pc_tot"],
                            x["random_tie"],
                        )
                    )

                    selected_staff = [x["n"] for x in scored[:3]]
                    tds[ca] = selected_staff
                    today_all.extend(selected_staff)

                nw[ds] = tds
                daily_all_staff.append(today_all)

            # Cập nhật số liệu tích lũy.
            for day_data in nw.values():
                for ca_name, names in day_data.items():
                    for person in names:
                        if person not in new_stats or not isinstance(new_stats[person], dict):
                            new_stats[person] = {
                                "ca": 0, "Sáng": 0, "Chiều": 0, "10h30": 0
                            }
                        for key in ["Sáng", "Chiều", "10h30"]:
                            new_stats[person].setdefault(key, 0)
                        new_stats[person]["ca"] = new_stats[person].get("ca", 0) + 1
                        if ca_name in ["Sáng", "Chiều", "10h30"]:
                            new_stats[person][ca_name] += 1

            return nw, new_stats
        except Exception as exc:
            app_logger.error(f"Lỗi thuật toán xếp lịch: {exc}")
            raise


    @staticmethod
    def _count_history_assignments(history: Dict[str, Any]) -> Dict[str, Dict[str, int]]:
        """Đếm số ca trong một bảng lịch, dùng để tính delta khi sửa tay."""
        counts: Dict[str, Dict[str, int]] = {}
        if not isinstance(history, dict):
            return counts
        for shifts in history.values():
            if not isinstance(shifts, dict):
                continue
            for ca, names in shifts.items():
                if not isinstance(names, list):
                    continue
                for raw_name in names:
                    if not isinstance(raw_name, str) or not raw_name.strip():
                        continue
                    name = raw_name.strip()
                    info = counts.setdefault(
                        name, {"ca": 0, "Sáng": 0, "Chiều": 0, "10h30": 0}
                    )
                    info["ca"] += 1
                    if ca in {"Sáng", "Chiều", "10h30"}:
                        info[ca] += 1
        return counts

    @staticmethod
    def preserve_stats_for_manual_edit(current_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Giữ nguyên mốc công bằng khi lịch chỉ được chỉnh thủ công.

        Lịch hiển thị có thể thêm/bớt/đổi người tùy ý, nhưng các thay đổi tay
        không được cộng/trừ vào ``stats`` mà thuật toán dùng để cân bằng các tuần sau.
        Trả về bản sao sâu để UI có thể rollback/lưu mà không dùng chung tham chiếu.
        """
        return copy.deepcopy(current_stats) if isinstance(current_stats, dict) else {}

    @staticmethod
    def apply_manual_edit_stats(
        old_history: Dict[str, Any],
        new_history: Dict[str, Any],
        current_stats: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Áp chênh lệch lịch sửa tay vào tích lũy hiện có.

        ``stats`` là số tích lũy qua nhiều tuần, nên không được rescan riêng
        bảng lịch hiện tại. Ta chỉ cộng/trừ phần chênh giữa lịch cũ và lịch mới.
        """
        old_counts = ScheduleService._count_history_assignments(old_history)
        new_counts = ScheduleService._count_history_assignments(new_history)

        result: Dict[str, Any] = {}
        for name, raw in (current_stats or {}).items():
            if isinstance(raw, dict):
                result[name] = raw.copy()
            else:
                total = raw if isinstance(raw, (int, float)) else 0
                result[name] = {"ca": int(total), "Sáng": 0, "Chiều": 0, "10h30": 0}

        all_names = set(old_counts) | set(new_counts)
        keys = ("ca", "Sáng", "Chiều", "10h30")
        for name in all_names:
            info = result.setdefault(name, {k: 0 for k in keys})
            for key in keys:
                try:
                    base = int(info.get(key, 0) or 0)
                except (TypeError, ValueError):
                    base = 0
                delta = new_counts.get(name, {}).get(key, 0) - old_counts.get(name, {}).get(key, 0)
                info[key] = max(0, base + delta)

        return result

    @staticmethod
    def diff_manual_schedule(old_history: Dict[str, Any], new_history: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Trả danh sách thay đổi gọn để ghi nhật ký sửa lịch."""
        changes: List[Dict[str, Any]] = []
        day_order = list(dict.fromkeys(list((old_history or {}).keys()) + list((new_history or {}).keys())))
        shift_order = ["Sáng", "Chiều", "10h30"]
        for day in day_order:
            old_shifts = (old_history or {}).get(day, {}) or {}
            new_shifts = (new_history or {}).get(day, {}) or {}
            extra = [k for k in dict.fromkeys(list(old_shifts.keys()) + list(new_shifts.keys())) if k not in shift_order]
            for shift in shift_order + extra:
                before = list(old_shifts.get(shift, []) or [])
                after = list(new_shifts.get(shift, []) or [])
                if before != after:
                    changes.append({
                        "day": day,
                        "shift": shift,
                        "before": before,
                        "after": after,
                    })
        return changes

    @staticmethod
    def find_multi_shift_assignments(history: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Tìm trường hợp một người xuất hiện ở từ 2 ca trở lên trong cùng ngày.

        Chỉ dùng để cảnh báo khi sửa tay; không tự chặn vì quản lý có thể chủ động
        xếp một người nhiều ca trong ngày. So khớp tên không phân biệt hoa/thường.
        """
        conflicts: List[Dict[str, Any]] = []
        if not isinstance(history, dict):
            return conflicts

        preferred_order = ["Sáng", "10h30", "Chiều"]
        for day, shifts in history.items():
            if not isinstance(shifts, dict):
                continue
            by_person: Dict[str, Dict[str, Any]] = {}
            shift_names = preferred_order + [
                key for key in shifts.keys() if key not in preferred_order
            ]
            for shift in shift_names:
                names = shifts.get(shift, [])
                if not isinstance(names, list):
                    continue
                for raw_name in names:
                    name = str(raw_name or "").strip()
                    if not name:
                        continue
                    key = name.casefold()
                    info = by_person.setdefault(key, {"name": name, "shifts": []})
                    if shift not in info["shifts"]:
                        info["shifts"].append(shift)

            for info in by_person.values():
                if len(info["shifts"]) >= 2:
                    conflicts.append({
                        "day": str(day),
                        "name": info["name"],
                        "shifts": list(info["shifts"]),
                    })
        return conflicts

    @staticmethod
    def new_multi_shift_assignments(
        old_history: Dict[str, Any], new_history: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Chỉ trả các trùng ca mới phát sinh hoặc tăng thêm sau lần sửa tay."""
        old = ScheduleService.find_multi_shift_assignments(old_history)
        new = ScheduleService.find_multi_shift_assignments(new_history)

        old_map = {
            (item["day"], str(item["name"]).casefold()): set(item.get("shifts", []))
            for item in old
        }
        result: List[Dict[str, Any]] = []
        for item in new:
            key = (item["day"], str(item["name"]).casefold())
            before = old_map.get(key, set())
            after = set(item.get("shifts", []))
            if len(after) >= 2 and (len(before) < 2 or after != before):
                result.append(item)
        return result

    @staticmethod
    def rescan_history(history: Dict[str, Any]) -> Dict[str, Any]:
        """Quét lại lịch sử trực để đếm lại thống kê từ đầu."""
        new_stats: Dict[str, Any] = {}
        for _, shifts in history.items():
            for ca, names in shifts.items():
                for n in names:
                    if not isinstance(n, str) or not n.strip():
                        continue
                    name = n.strip()
                    if name not in new_stats:
                        new_stats[name] = {
                            "ca": 0, "Sáng": 0, "Chiều": 0, "10h30": 0
                        }
                    new_stats[name]["ca"] += 1
                    if ca in ["Sáng", "Chiều", "10h30"]:
                        new_stats[name][ca] += 1
        return new_stats
