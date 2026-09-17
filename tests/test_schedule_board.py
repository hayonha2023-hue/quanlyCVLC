from views.schedule_board import board_html


def test_names_and_dates_are_escaped_and_extra_shifts_preserved():
    html=board_html({'<Ngày>':{'Ca bổ sung':['<script>name</script>'],'Sáng':[]}})
    assert '<script>' not in html and '&lt;script&gt;' in html
    assert '&lt;Ngày&gt;' in html and 'Ca bổ sung' in html
    assert 'Chưa phân công' in html


def test_search_keeps_teammates_and_highlights_matching_person():
    html=board_html({'Thứ 2':{'Sáng':['An','Bình']},'Thứ 3':{'Chiều':['Cúc']}},'bÌnH')
    assert 'Thứ 2' in html and 'Thứ 3' not in html
    assert '>An</span>' in html and 'schedule-person match">Bình' in html
    assert '2 người' in html


def test_shift_order_and_empty_search_result():
    html=board_html({'Thứ 2':{'Chiều':['A'],'Sáng':['B'],'10h30':['C']}})
    assert html.index('Ca Sáng') < html.index('Ca 10h30') < html.index('Ca Chiều')
    assert board_html({'Thứ 2':{'Sáng':['An']}},'không có')==''
