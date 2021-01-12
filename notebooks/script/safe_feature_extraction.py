#!/usr/bin/env python
# coding: utf-8

# ## Pre-requisities
# 
# - wget http://nlp.stanford.edu/software/stanford-postagger-full-2016-10-31.zip
# - put in `references/re_2017_johann_et-al` (private files, licensed by the author)
# - Update in `FE_Safe.py` variable `path_to_model` and `path_to_jar` with absolute path to its directory
# 
#  
# **Required libraries**:
# ```
# import nltk
# nltk.download('stopwords')
# nltk.download('punkt')
# ```

# Python path referencing
import os
import sys

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path+"/references/re_2017_johann_et-al")
    
import FE_SAFE as fs
# print(sys.path)


get_ipython().run_cell_magic('time', '', '\nexample_description = """\n        WhatsApp Messenger is a FREE messaging app available for Android and other smartphones. WhatsApp uses your phones Internet connection (4G/3G/2G/EDGE or Wi-Fi, as available) to let you message and call friends and family. Switch from SMS to WhatsApp to send and receive messages, calls, photos, videos, documents, and Voice Messages.\n        WHY USE WHATSAPP\n    """\n\n#     feature_extractor = SAFE()\nfeature_extractor = fs.SAFE()\nfeature_extractor.extract_from_description(example_description)')


get_ipython().run_cell_magic('time', '', '## Extract from a single descriptions\n###########\nexample_description = """\n            WhatsApp Messenger is a FREE messaging app available for Android and other smartphones. WhatsApp uses your phones Internet connection (4G/3G/2G/EDGE or Wi-Fi, as available) to let you message and call friends and family. Switch from SMS to WhatsApp to send and receive messages, calls, photos, videos, documents, and Voice Messages.\n            WHY USE WHATSAPP:\n\n            • NO FEES: WhatsApp uses your phones Internet connection (4G/3G/2G/EDGE or Wi-Fi, as available) to let you message and call friends and family, so you dont have to pay for every message or call.* There are no subscription fees to use WhatsApp.\n\n            • MULTIMEDIA: Send and receive photos, videos, documents, and Voice Messages.\n\n            • FREE CALLS: Call your friends and family for free with WhatsApp Calling, even if theyre in another country.* WhatsApp calls use your phones Internet connection rather than your cellular plans voice minutes. (Note: Data charges may apply. Contact your provider for details. Also, you cant access 911 and other emergency service numbers through WhatsApp).\n\n            • GROUP CHAT: Enjoy group chats with your contacts so you can easily stay in touch with your friends or family.\n\n            • WHATSAPP WEB: You can also send and receive WhatsApp messages right from your computers browser.\n\n            • NO INTERNATIONAL CHARGES: Theres no extra charge to send WhatsApp messages internationally. Chat with your friends around the world and avoid international SMS charges.*\n\n            • SAY NO TO USERNAMES AND PINS: Why bother having to remember yet another username or PIN? WhatsApp works with your phone number, just like SMS, and integrates seamlessly with your phones existing address book.\n\n            • ALWAYS LOGGED IN: With WhatsApp, youre always logged in so you dont miss messages. No more confusion about whether youre logged in or logged out.\n\n            • QUICKLY CONNECT WITH YOUR CONTACTS: Your address book is used to quickly and easily connect you with your contacts who have WhatsApp so theres no need to add hard-to-remember usernames.\n\n            • OFFLINE MESSAGES: Even if you miss your notifications or turn off your phone, WhatsApp will save your recent messages until the next time you use the app.\n\n            • AND MUCH MORE: Share your location, exchange contacts, set custom wallpapers and notification sounds, email chat history, broadcast messages to multiple contacts at once, and more!\n\n            *Data charges may apply. Contact your provider for details.\n\n            ---------------------------------------------------------\n            Were always excited to hear from you! If you have any feedback, questions, or concerns, please email us at:\n\n            android-support@whatsapp.com\n\n            or follow us on twitter:\n\n            http://twitter.com/WhatsApp\n            @WhatsApp\n            ---------------------------------------------------------\n        """\n\nfeature_extractor = fs.SAFE()\nfeature_extractor.extract_from_description(example_description)')




