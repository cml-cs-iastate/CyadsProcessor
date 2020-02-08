from processor.encoding_helpers import reconstruct_utf8_list_from_str_utf8_bstr_saved_as_latin1_swedish, \
    reconstruct_utf8_str_from_str_utf8_bstr_also_latin1_swedish


def test_keywords_case1():
    test_str = r'''["AP News Video CR Editor\'s Picks", \'English/Natsound\', \'16:9\']'''
    answer = ["AP News Video CR Editor's Picks", 'English/Natsound', '16:9']
    assert reconstruct_utf8_list_from_str_utf8_bstr_saved_as_latin1_swedish(test_str) == answer


def test_empty_keywords_case1():
    test_str = r""
    answer = []
    assert reconstruct_utf8_list_from_str_utf8_bstr_saved_as_latin1_swedish(test_str) == answer


def test_empty_keywords_empty_list():
    test_str = r"[]"
    answer = []
    assert reconstruct_utf8_list_from_str_utf8_bstr_saved_as_latin1_swedish(test_str) == answer


def test_str_reconstruct_case1():
    test_str = r'''Rep. Gowdy on Trump "Spygate" claims: Informants used "all day, every day"'''
    answer = 'Rep. Gowdy on Trump "Spygate" claims: Informants used "all day, every day"'
    assert reconstruct_utf8_str_from_str_utf8_bstr_also_latin1_swedish(test_str) == answer


def test_empty_str_case1():
    test_str = r""
    answer = ""
    assert reconstruct_utf8_str_from_str_utf8_bstr_also_latin1_swedish(test_str) == answer


def test_escaped_str_case1():
    test_str = r"Lawrence: President Donald Trump's \xe2\x80\x98Lie\xe2\x80\x99 Infiltrates Language"
    answer = r"Lawrence: President Donald Trump's ‘Lie’ Infiltrates Language"
    assert reconstruct_utf8_str_from_str_utf8_bstr_also_latin1_swedish(test_str) == answer


def test_str_decode_case2():
    test_str = r"\xf0\x9f\x94\xb5 Watch this video all the way through - you will miss too much if you watch only the first few minutes! Pastor Steve Cioccolanti downloads 5 of the Biggest REVELATIONS from the Singapore Summit/ Sentosa Agreement between Donald Trump and Kim Jong-Un, with revelations about Dennis Rodman, and a message for South Korean pastors. \n------------------------------- \n\nMENTIONED IN THIS VIDEO\n\xe2\x9c\x85 Join Discover Church Online via PATREON: https://www.patreon.com/cioccolanti (t"
    answer = "🔵 Watch this video all the way through - you will miss too much if you watch only the first few minutes! Pastor Steve Cioccolanti downloads 5 of the Biggest REVELATIONS from the Singapore Summit/ Sentosa Agreement between Donald Trump and Kim Jong-Un, with revelations about Dennis Rodman, and a message for South Korean pastors. \n------------------------------- \n\nMENTIONED IN THIS VIDEO\n✅ Join Discover Church Online via PATREON: https://www.patreon.com/cioccolanti (t"
    assert reconstruct_utf8_str_from_str_utf8_bstr_also_latin1_swedish(test_str) == answer


def test_already_utf8_is_the_same_with_tick():
    test_str = "there's"
    answer = "there's"
    assert reconstruct_utf8_str_from_str_utf8_bstr_also_latin1_swedish(test_str) == answer


def test_multiline_str_case1():
    test_str = """Donald Trump is set to meet Vladimir Putin in Helsinki on July the 16th. And the US President says he's sure the meeting will go smoothly, and warned against scaremongering. READ MORE: https://on.rt.com/9980

Check out http://rt.com

RT LIVE http://rt.com/on-air

Subscribe to RT! http://www.youtube.com/subscription_c...

Like us on Facebook http://www.facebook.com/RTnews
Follow us on Telegram https://t.me/rtintl
Follow us on VK https://vk.com/rt_international
Follow us on Twitter http://twitter.com/RT_com
Follow us on Instagram http://instagram.com/rt
Follow us on"""

    answer = """Donald Trump is set to meet Vladimir Putin in Helsinki on July the 16th. And the US President says he's sure the meeting will go smoothly, and warned against scaremongering. READ MORE: https://on.rt.com/9980

Check out http://rt.com

RT LIVE http://rt.com/on-air

Subscribe to RT! http://www.youtube.com/subscription_c...

Like us on Facebook http://www.facebook.com/RTnews
Follow us on Telegram https://t.me/rtintl
Follow us on VK https://vk.com/rt_international
Follow us on Twitter http://twitter.com/RT_com
Follow us on Instagram http://instagram.com/rt
Follow us on"""
    assert reconstruct_utf8_str_from_str_utf8_bstr_also_latin1_swedish(test_str) == answer


def test_str_case2():
    test_str = "“MediaBuzz’ host Howard Kurtz on the loud call from prominent Republicans to vote for Democrats."
    answer = "“MediaBuzz’ host Howard Kurtz on the loud call from prominent Republicans to vote for Democrats."
    assert reconstruct_utf8_str_from_str_utf8_bstr_also_latin1_swedish(test_str) == answer


def test_str_case3():
    test_str = """🔵 Watch this video all the way through - you will miss too much if you watch only the first few minutes! Pastor Steve Cioccolanti downloads 5 of the Biggest REVELATIONS from the Singapore Summit/ Sentosa Agreement between Donald Trump and Kim Jong-Un, with revelations about Dennis Rodman, and a message for South Korean pastors. 
------------------------------- 

MENTIONED IN THIS VIDEO
✅ Join Discover Church Online via PATREON: https://www.patreon.com/cioccolanti (this is the first step to build clean social media)
✅ LIVESTREAM the End Time Conference with Bill Salus and Steve Cioccolanti: https://stevecioccolanti.eventbrite.com (after 23 June, go to www.discover.org.au/bookshop for replay) 
✅ GIVE LAND to Discover Church: info@discover.org.au
✅ DONATE via PayPal: https://www.paypal.me/DiscoverChurch
✅ TRANSLATORS (Korean or any foreign language) who'd like to volunteer, email: info@discover.org.au, subject "Translator" 
✅ BUSINESSMEN wanting to bring God into North Korea, email: info@discover.org.au, subject: "Opportunity in Korea", with your LinkedIn profile
✅ PASTORS wishing to invite Pastor Steve to minister in their church: http://www.discover.org.au/invite
🔵 4 BOOKS by PASTOR Steve CIOCCOLANTI (Amazon fastest for North Americans. Discover Ministries best quality & cheapest for all other nations)
✅ FROM BUDDHA TO JESUS (in 7 languages) http://amazon.com/author/newyorktimes...
✅ THE DIVINE CODE FROM 1 to 2020 (out of stock) 
✅ 30 DAYS TO A NEW YOU https://discover.org.au/bookshop/book...
✅ 12 KEYS TO A GOOD RELATIONSHIP WITH GOD (Children's Book) https://discover.org.au/bookshop/book...
-------------------------------- 
🔵 MUSIC CREDIT: Original music made exclusively for Discover Ministries by world-class composer Tom Hanke. Check him out! 
http://www.tomhankemusic.com
-------------------------------- 

✅ 4 STEPS TO JOIN DISCOVER CHURCH ONLINE: 

🔵 1) Follow us on Patreon and become a Patron: https://www.patreon.com/cioccolanti You will get audios, videos, posts and photos not shared on any other social media.

🔵 2) Tithe to your home church and give offerings on Discover Church Online. Some Christians have been mistaught that tithing is not found in the New Testament, which is false doctrine: read Luke 11:42 and Hebrews 7:8. God teaches that the tithe (10% of income) is His and must be returned to the place that feeds you spiritually. If you reside in a geographical location without a Bible-teaching church, you may treat us as your online church. 

🔵 Separate to tithes, you can sow offerings to any ministry that feeds you according to Galatians 6:6. Offerings can be any amount. We believe the $58 seed is prophetic. Contribute to God's ministry: http://www.discover.org.au/partner 

🔵 3) Pray with and for Discover Ministries (Colossians 4:3, 2 Corinthians 1:11) Here are some model prayers you can start with: http://www.discover.org.au/pray 

🔵 4) Spread Jesus, the Word of God, to your family and friends. YouTube links are one easy way. Books and DVDs are another way. Before giving Christian books or videos, first pray in faith for the people you want to be saved. For help refer to a model prayer from Pastor Steve’s life called “6 Steps” and use it right away!

✅ BE PART of an END-TIME NETWORK of like-minded believers who want to collaborate and have massive impact on the world online and offline. Join DISCOVER CHURCH ONLINE today! 

------------------------------- 
✅ Subscribe to our friendly E-NEWS 
http://www.discover.org.au/subscribe
--------------------------------  

✅ BUY Christian books, DVDs, CDs, MP4s, MP3s, Gifts: http://www.discover.org.au/bookshop 

🔵 A GUIDE TO THE MILLENNIUM (MP4): https://discover.org.au/bookshop/mp4/...
🔵  500 YEARS SINCE MARTIN LUTHER'S INCOMPLETE REFORMATION (1DVD OR CD): https://discover.org.au/bookshop/inde...
🔵 A CHRISTIAN TOUR OF ISRAEL - NEW! (Play-on-Demand video): https://discover.org.au/bookshop/repl...
🔵 2 SECRETS OF THE JEWS: From Abraham to Modern Israel (1 DVD) https://discover.org.au/bookshop/dvd-...

✅ STREAM videos on demand: https://vimeo.com/stevecioccolanti/vo...
✅ FIND freedom in Christ's Life & Teachings. 
✅ Your SUPPORT of this Christian ministry is GREATLY appreciated.
"""
    answer = """🔵 Watch this video all the way through - you will miss too much if you watch only the first few minutes! Pastor Steve Cioccolanti downloads 5 of the Biggest REVELATIONS from the Singapore Summit/ Sentosa Agreement between Donald Trump and Kim Jong-Un, with revelations about Dennis Rodman, and a message for South Korean pastors. 
------------------------------- 

MENTIONED IN THIS VIDEO
✅ Join Discover Church Online via PATREON: https://www.patreon.com/cioccolanti (this is the first step to build clean social media)
✅ LIVESTREAM the End Time Conference with Bill Salus and Steve Cioccolanti: https://stevecioccolanti.eventbrite.com (after 23 June, go to www.discover.org.au/bookshop for replay) 
✅ GIVE LAND to Discover Church: info@discover.org.au
✅ DONATE via PayPal: https://www.paypal.me/DiscoverChurch
✅ TRANSLATORS (Korean or any foreign language) who'd like to volunteer, email: info@discover.org.au, subject "Translator" 
✅ BUSINESSMEN wanting to bring God into North Korea, email: info@discover.org.au, subject: "Opportunity in Korea", with your LinkedIn profile
✅ PASTORS wishing to invite Pastor Steve to minister in their church: http://www.discover.org.au/invite
🔵 4 BOOKS by PASTOR Steve CIOCCOLANTI (Amazon fastest for North Americans. Discover Ministries best quality & cheapest for all other nations)
✅ FROM BUDDHA TO JESUS (in 7 languages) http://amazon.com/author/newyorktimes...
✅ THE DIVINE CODE FROM 1 to 2020 (out of stock) 
✅ 30 DAYS TO A NEW YOU https://discover.org.au/bookshop/book...
✅ 12 KEYS TO A GOOD RELATIONSHIP WITH GOD (Children's Book) https://discover.org.au/bookshop/book...
-------------------------------- 
🔵 MUSIC CREDIT: Original music made exclusively for Discover Ministries by world-class composer Tom Hanke. Check him out! 
http://www.tomhankemusic.com
-------------------------------- 

✅ 4 STEPS TO JOIN DISCOVER CHURCH ONLINE: 

🔵 1) Follow us on Patreon and become a Patron: https://www.patreon.com/cioccolanti You will get audios, videos, posts and photos not shared on any other social media.

🔵 2) Tithe to your home church and give offerings on Discover Church Online. Some Christians have been mistaught that tithing is not found in the New Testament, which is false doctrine: read Luke 11:42 and Hebrews 7:8. God teaches that the tithe (10% of income) is His and must be returned to the place that feeds you spiritually. If you reside in a geographical location without a Bible-teaching church, you may treat us as your online church. 

🔵 Separate to tithes, you can sow offerings to any ministry that feeds you according to Galatians 6:6. Offerings can be any amount. We believe the $58 seed is prophetic. Contribute to God's ministry: http://www.discover.org.au/partner 

🔵 3) Pray with and for Discover Ministries (Colossians 4:3, 2 Corinthians 1:11) Here are some model prayers you can start with: http://www.discover.org.au/pray 

🔵 4) Spread Jesus, the Word of God, to your family and friends. YouTube links are one easy way. Books and DVDs are another way. Before giving Christian books or videos, first pray in faith for the people you want to be saved. For help refer to a model prayer from Pastor Steve’s life called “6 Steps” and use it right away!

✅ BE PART of an END-TIME NETWORK of like-minded believers who want to collaborate and have massive impact on the world online and offline. Join DISCOVER CHURCH ONLINE today! 

------------------------------- 
✅ Subscribe to our friendly E-NEWS 
http://www.discover.org.au/subscribe
--------------------------------  

✅ BUY Christian books, DVDs, CDs, MP4s, MP3s, Gifts: http://www.discover.org.au/bookshop 

🔵 A GUIDE TO THE MILLENNIUM (MP4): https://discover.org.au/bookshop/mp4/...
🔵  500 YEARS SINCE MARTIN LUTHER'S INCOMPLETE REFORMATION (1DVD OR CD): https://discover.org.au/bookshop/inde...
🔵 A CHRISTIAN TOUR OF ISRAEL - NEW! (Play-on-Demand video): https://discover.org.au/bookshop/repl...
🔵 2 SECRETS OF THE JEWS: From Abraham to Modern Israel (1 DVD) https://discover.org.au/bookshop/dvd-...

✅ STREAM videos on demand: https://vimeo.com/stevecioccolanti/vo...
✅ FIND freedom in Christ's Life & Teachings. 
✅ Your SUPPORT of this Christian ministry is GREATLY appreciated.
"""
    assert reconstruct_utf8_str_from_str_utf8_bstr_also_latin1_swedish(test_str) == answer

def test_nonenglish_case1():
    answer = """🇪🇷 🇪🇹 Eritrea delegation arrives in Ethiopia ahead of landmark talks | Al Jazeera English"""
