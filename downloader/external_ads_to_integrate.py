#!/usr/bin/env python
# coding: utf-8

# In[115]:


import csv
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
from urllib import parse


# In[36]:


urls = []
with open("/home/alex/external_urls.csv") as f:
    reader = csv.reader(f)
    for line in reader:
        url = line[0].strip()
        urls.append(url)
sorted_urls = sorted(urls)


# In[37]:


s = set()
for url in urls:
    host = urlparse(url).hostname
    s.add(host)
    if host == "www.youtube.com":
        print(url)
print(s)


# In[38]:


url_parts[2:6]


# In[124]:


def _extract_parts(url: str) -> PurePosixPath:
    parsed = urlparse(url)
    return PurePosixPath(unquote(parsed.path)).parts


def handle_cbsadsales_a_akamaihd(url: str) -> str:
    url_parts = _extract_parts(url)
    id_pt1 = url_parts[1]
    id_pt2 = url_parts[2]
    return f"{id_pt1}-{id_pt2}"
    
def handle_cdn_flashtalking(url: str):
    url_parts = _extract_parts(url)
    id_pt1 = url_parts[1]
    id_pt2 = url_parts[2]
    return f"{id_pt1}-{id_pt2}"

def handle_cdn_jivox(url: str):
    url_parts = _extract_parts(url)
    return '-'.join(url_parts[1:4])

def handle_ssl_cdn_turner(url: str) -> str:
    url_parts = _extract_parts(url)
    return '-'.join(url_parts[4:8])

def handle_cdn_video_abc(url: str) -> str:
    url_parts = _extract_parts(url)
    return url_parts[3]

def handle_cdn1_extremereach(url: str) -> str:
    url_parts = _extract_parts(url)
    return '-'.join(url_parts[2:6])

def handle_ad_wsodcdn(url: str) -> str:
    url_parts = _extract_parts(url)
    id_pt1 = url_parts[3]
    id_pt2 = url_parts[8]
    return f"{id_pt1}-{id_pt2}"

def handle_ads_pd_nbcuni(url: str) -> str:
    url_parts = _extract_parts(url)
    id_pt1 = url_parts[2]
    id_pt2 = url_parts[3]
    return f"{id_pt1}-{id_pt2}"

def handle_gcdn_2mdn(url: str) -> str:
    url_parts = _extract_parts(url)
    if url_parts[2] != "id" and url_parts[1] != "videoplayback":
        raise AssertionError(f"/videoplayback/id does not begin the url={url}")
    id_offset = url_parts.index("id")
    file_id = url_parts[id_offset + 1]
    file_ext = url_parts[-1]
    return f"{file_id}-{file_ext}"

def handle_innovid(url: str) -> str:
    url_parts = _extract_parts(url)
    id_pt1 = url_parts[-3]
    id_pt2 = url_parts[-2]
    id_pt3 = url_parts[-1]
    return f"{id_pt1}-{id_pt2}-{id_pt3}"

def handle_cdn01_basis(url: str) -> str:
    url_parts = _extract_parts(url)
    return '-'.join(url_parts[1:4])

def handle_i_r1_cdn(url: str) -> str:
    url_parts = _extract_parts(url)
    return '-'.join(url_parts[1:5])

def handle_nbcotsadops_akamaized(url: str) -> str:
    url_parts = _extract_parts(url)
    return url_parts[2]

def handle_olyhdliveextraads_amd_akamaized(url: str) -> str:
    url_parts = _extract_parts(url)
    return '-'.join(url_parts[1:5])

def handle_playtime_tubemogul(url: str) -> str:
    url_parts = _extract_parts(url)
    return url_parts[2]

def handle_redirector_gvt1(url: str) -> str:
    url_parts = _extract_parts(url)
    id_offset = url_parts.index("id")
    id_pt1 = url_parts[id_offset + 1]
    id_pt2 = url_parts[-1]
    return f"{id_pt1}-{id_pt2}"

def handle_s2_adform(url: str) -> str:
    url_parts = _extract_parts(url)
    id_pt1 = url_parts[-2]
    id_pt2 = url_parts[-1]
    return f"{id_pt1}-{id_pt2}"

def handle_secure_ds_serving_sys(url: str) -> str:
    url_parts = _extract_parts(url)
    site_num = url_parts[-3]
    assert "Site-" in site_num
    vid_type = url_parts[-2]
    assert "Type-" in vid_type
    filename = url_parts[-1]
    return f"{site_num}-{vid_type}-{filename}"

def handle_shunivision_a_akamaihd(url: str) -> str:
    url_parts = _extract_parts(url)
    return '-'.join(url_parts[1:])

def handle_v_adsrvr(url: str) -> str:
    url_parts = _extract_parts(url)
    return '-'.join(url_parts[1:])

def handle_washingtonpost(url: str) -> str:
    url_parts = _extract_parts(url)
    return unquote(url_parts[-1])

def handle_extended_youtube(url: str) -> str:
    return parse.parse_qs(urlparse(url).query)["v"][0]

handlers = {
    "ad.wsodcdn.com": handle_ad_wsodcdn,
    "ads-pd.nbcuni.com": handle_ads_pd_nbcuni,
    "amd-ssl.cdn.turner.com": handle_ssl_cdn_turner,
    "cbsadsales-a.akamaihd.net": handle_cbsadsales_a_akamaihd,
    "cdn.flashtalking.com": handle_cdn_flashtalking,
    "cdn.jivox.com": handle_cdn_jivox,
    "cdn1.extremereach.io": handle_cdn1_extremereach,
    "cdn.video.abc.com": handle_cdn_video_abc,
    "gcdn.2mdn.net": handle_gcdn_2mdn,
    "i.r1-cdn.net": handle_i_r1_cdn,
    "cdn01.basis.net": handle_cdn01_basis,
    "nbcotsadops.akamaized.net": handle_nbcotsadops_akamaized,
    "olyhdliveextraads-amd.akamaized.net": handle_olyhdliveextraads_amd_akamaized,
    "playtime.tubemogul.com": handle_playtime_tubemogul,
    "redirector.gvt1.com": handle_redirector_gvt1,
    "s-static.innovid.com": handle_innovid,
    "s2.adform.net": handle_s2_adform,
    "secure-ds.serving-sys.com": handle_secure_ds_serving_sys,
    "shunivision-a.akamaihd.net": handle_shunivision_a_akamaihd,
    "v.adsrvr.org": handle_v_adsrvr,
    "www.washingtonpost.com": handle_washingtonpost,
    "www.youtube.com": handle_extended_youtube,
    }


# In[125]:


for url in sorted_urls:
    if "gcdn.2mdn.net" in url:
        parsed = urlparse(url)
        hostname = parsed.hostname
        print(url)
        result = handlers[hostname](url)
        if result is not None and result != "":
            print(result)


# In[126]:



class HostProcess:
def __init__(self, url: str, handlers: dict):
    self.url = url
    self.netloc = urlparse(url).netloc
    self.handlers = handlers

def unique_file_url(self) -> str:
    filename = self.handlers[self.netloc](self.url)
    return f"{self.netloc}-{filename}"


# In[127]:


uniq_ads = set()
for url in sorted_urls:
    process = HostProcess(url, handlers)
    result = process.unique_file_url()
    assert result is not None and result != ""
    uniq_ads.add(result)
print(len(uniq_ads))


# In[128]:


for file in uniq_ads:
    print(file)


# In[228]:


HostProcess.__dict__


# In[7]:


for index, url in enumerate(sorted((urls))):
    try:
        handler_gcdn_2mdn(url)
    except AssertionError as e:
        print(f"index {index}, {e}")


# In[ ]:




