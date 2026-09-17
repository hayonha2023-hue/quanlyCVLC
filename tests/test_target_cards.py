from views.target_cards import display_number, cards_html


def test_local_numbers_keep_precision_and_missing_is_not_zero():
    assert display_number(1500000)=='1.500.000'
    assert display_number(12.56789)=='12,56789'
    assert display_number(-1234.5)=='-1.234,5'
    assert display_number('1.500.000')=='1.500.000'
    assert display_number(None)=='—'
    assert display_number('')=='—'
    assert display_number(0)=='0'


def test_cards_keep_scopes_and_escape_text_without_assuming_currency():
    html=cards_html([{'Chỉ số':'<Thuốc>','Ngày / người':1250,'Tháng / người':30000}],
                    [('Ngày / người','Mỗi người / ngày','goal'),('Tháng / người','Mỗi người / tháng','neutral')])
    assert '&lt;Thuốc&gt;' in html and '<Thuốc>' not in html
    assert '1.250' in html and '30.000' in html
    assert 'Mỗi người / ngày' in html and 'Mỗi người / tháng' in html
    assert 'đồng' not in html
