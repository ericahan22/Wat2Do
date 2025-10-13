from services.openai_service import extract_events_from_caption

# Test data
post = {
    "id": "3721572472337849724_1541676532",
    "owner": {
        "pk": "1541676532",
        "id": "1541676532",
        "transparency_product": None,
        "transparency_product_enabled": False,
        "transparency_label": None,
        "username": "wloo.dboat",
        "ai_agent_owner_username": None,
        "profile_pic_url": "https://scontent-iad3-1.cdninstagram.com/v/t51.2885-19/340840539_1165496987467636_2379394817402339730_n.jpg?stp=dst-jpg_s150x150_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby43NTUuYzIifQ&_nc_ht=scontent-iad3-1.cdninstagram.com&_nc_cat=104&_nc_oc=Q6cZ2QFakGqpqRaqvBSF1Tf8h04TdNo057GigYrPg3CyZFDeCkj3SFTWGzxT9TMLJW7K0oI&_nc_ohc=AIRdFDXeOmIQ7kNvwEv4hZS&_nc_gid=Tjkgx5MQrPqgeF4wnZdjLQ&edm=APNOSGoBAAAA&ccb=7-5&oh=00_AfZgL24_QrCJPRRNv_1QcOFEYKdKVnoN3IRe7Q7V878lGA&oe=68CCAD59&_nc_sid=ca40e6",
        "show_account_transparency_details": True,
        "__typename": "XDTUserDict",
        "is_private": False,
        "friendship_status": {"following": True},
    },
    "view_state_item_type": None,
    "brs_severity": None,
    "pk": "3721572472337849724",
    "inventory_source": "media_or_ad",
    "logging_info_token": (
        "GCAyMDdiZDNiYTgwYTU0OTU3ODk5YWRhNzNmNjlkN2E4Ykbiq7eMDSbiq7eMDRgDbmNnFuCrt4wNAA=="
    ),
    "explore": None,
    "main_feed_carousel_starting_media_id": None,
    "carousel_media": None,
    "audience": None,
    "is_seen": False,
    "media_type": 1,
    "original_height": 1350,
    "original_width": 1080,
    "is_shared_from_basel": None,
    "has_liked": False,
    "open_carousel_submission_state": None,
    "media_overlay_info": None,
    "code": "DOlrnIjkd18",
    "user": {
        "pk": "1541676532",
        "profile_pic_url": "https://scontent-iad3-1.cdninstagram.com/v/t51.2885-19/340840539_1165496987467636_2379394817402339730_n.jpg?stp=dst-jpg_s150x150_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby43NTUuYzIifQ&_nc_ht=scontent-iad3-1.cdninstagram.com&_nc_cat=104&_nc_oc=Q6cZ2QFakGqpqRaqvBSF1Tf8h04TdNo057GigYrPg3CyZFDeCkj3SFTWGzxT9TMLJW7K0oI&_nc_ohc=AIRdFDXeOmIQ7kNvwEv4hZS&_nc_gid=Tjkgx5MQrPqgeF4wnZdjLQ&edm=APNOSGoBAAAA&ccb=7-5&oh=00_AfZgL24_QrCJPRRNv_1QcOFEYKdKVnoN3IRe7Q7V878lGA&oe=68CCAD59&_nc_sid=ca40e6",
        "username": "wloo.dboat",
        "id": "1541676532",
        "is_unpublished": False,
        "live_broadcast_visibility": None,
        "live_broadcast_id": None,
        "hd_profile_pic_url_info": {
            "url": "https://scontent-iad3-1.cdninstagram.com/v/t51.2885-19/340840539_1165496987467636_2379394817402339730_n.jpg?efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby43NTUuYzIifQ&_nc_ht=scontent-iad3-1.cdninstagram.com&_nc_cat=104&_nc_oc=Q6cZ2QFakGqpqRaqvBSF1Tf8h04TdNo057GigYrPg3CyZFDeCkj3SFTWGzxT9TMLJW7K0oI&_nc_ohc=AIRdFDXeOmIQ7kNvwEv4hZS&_nc_gid=Tjkgx5MQrPqgeF4wnZdjLQ&edm=APNOSGoBAAAA&ccb=7-5&oh=00_AfakE2Wyiyf593tKYDDnD-8hFaW-KSr6ENdp2wG4BHknFQ&oe=68CCAD59&_nc_sid=ca40e6"
        },
        "full_name": "UWaterloo Dragon Boat",
        "is_verified": False,
        "friendship_status": {"following": True, "is_feed_favorite": False},
        "is_private": False,
        "__typename": "XDTUserDict",
        "is_embeds_disabled": False,
        "latest_reel_media": 0,
    },
    "carousel_parent_id": None,
    "display_uri": None,
    "is_dash_eligible": None,
    "number_of_qualities": None,
    "video_dash_manifest": None,
    "video_versions": None,
    "accessibility_caption": (
        "Photo by UWaterloo Dragon Boat on September 14, 2025. May be an image of 8 people, "
        "poster and text that says 'LEARN UWDBC AT CLUBS FAIR DRAGON BOT + SEPT 18T 11am- 3pT "
        "MEET OUR EXECS :) SEPT 19TH 11am- 11am-2pm 2pm SLC RHKK\u0438Ebe VRKAA hinOek CUSHOU.COM'."
    ),
    "image_versions2": {
        "candidates": [
            {
                "url": "https://scontent-iad3-2.cdninstagram.com/v/t51.2885-15/548964154_18527355667044533_1511165445211038365_n.jpg?stp=dst-jpg_e35_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQuaW1hZ2VfdXJsZ2VuLjEwODB4MTM1MC5zZHIuZjgyNzg3LmRlZmF1bHRfaW1hZ2UuYzIifQ&_nc_ht=scontent-iad3-2.cdninstagram.com&_nc_cat=105&_nc_oc=Q6cZ2QFakGqpqRaqvBSF1Tf8h04TdNo057GigYrPg3CyZFDeCkj3SFTWGzxT9TMLJW7K0oI&_nc_ohc=3EuKCmVNwusQ7kNvwHLy7MK&_nc_gid=Tjkgx5MQrPqgeF4wnZdjLQ&edm=APNOSGoBAAAA&ccb=7-5&ig_cache_key=MzcyMTU3MjQ3MjMzNzg0OTcyNA%3D%3D.3-ccb7-5&oh=00_AfZi_PI7J3SZ43KqkIK3Q_5xHlwPelkftjzu5qrZ0kXN3w&oe=68CCC2FD&_nc_sid=ca40e6",
                "height": 1350,
                "width": 1080,
            },
            {
                "url": "https://scontent-iad3-2.cdninstagram.com/v/t51.2885-15/548964154_18527355667044533_1511165445211038365_n.jpg?stp=dst-jpg_e35_p720x720_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQuaW1hZ2VfdXJsZ2VuLjEwODB4MTM1MC5zZHIuZjgyNzg3LmRlZmF1bHRfaW1hZ2UuYzIifQ&_nc_ht=scontent-iad3-2.cdninstagram.com&_nc_cat=105&_nc_oc=Q6cZ2QFakGqpqRaqvBSF1Tf8h04TdNo057GigYrPg3CyZFDeCkj3SFTWGzxT9TMLJW7K0oI&_nc_ohc=3EuKCmVNwusQ7kNvwHLy7MK&_nc_gid=Tjkgx5MQrPqgeF4wnZdjLQ&edm=APNOSGoBAAAA&ccb=7-5&ig_cache_key=MzcyMTU3MjQ3MjMzNzg0OTcyNA%3D%3D.3-ccb7-5&oh=00_AfZpnA2w4w3j1MF-w-eg9I3ujLIoaoxbXkSo-Q76n22mJw&oe=68CCC2FD&_nc_sid=ca40e6",
                "height": 900,
                "width": 720,
            },
            {
                "url": "https://scontent-iad3-2.cdninstagram.com/v/t51.2885-15/548964154_18527355667044533_1511165445211038365_n.jpg?stp=dst-jpg_e35_p640x640_sh0.08_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQuaW1hZ2VfdXJsZ2VuLjEwODB4MTM1MC5zZHIuZjgyNzg3LmRlZmF1bHRfaW1hZ2UuYzIifQ&_nc_ht=scontent-iad3-2.cdninstagram.com&_nc_cat=105&_nc_oc=Q6cZ2QFakGqpqRaqvBSF1Tf8h04TdNo057GigYrPg3CyZFDeCkj3SFTWGzxT9TMLJW7K0oI&_nc_ohc=3EuKCmVNwusQ7kNvwHLy7MK&_nc_gid=Tjkgx5MQrPqgeF4wnZdjLQ&edm=APNOSGoBAAAA&ccb=7-5&ig_cache_key=MzcyMTU3MjQ3MjMzNzg0OTcyNA%3D%3D.3-ccb7-5&oh=00_AfY7uZFdNXQ4PH2-0AfW4XhzcSOAbU5HeZvdx_jUhwn6fg&oe=68CCC2FD&_nc_sid=ca40e6",
                "height": 800,
                "width": 640,
            },
            {
                "url": "https://scontent-iad3-2.cdninstagram.com/v/t51.2885-15/548964154_18527355667044533_1511165445211038365_n.jpg?stp=dst-jpg_e35_p480x480_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQuaW1hZ2VfdXJsZ2VuLjEwODB4MTM1MC5zZHIuZjgyNzg3LmRlZmF1bHRfaW1hZ2UuYzIifQ&_nc_ht=scontent-iad3-2.cdninstagram.com&_nc_cat=105&_nc_oc=Q6cZ2QFakGqpqRaqvBSF1Tf8h04TdNo057GigYrPg3CyZFDeCkj3SFTWGzxT9TMLJW7K0oI&_nc_ohc=3EuKCmVNwusQ7kNvwHLy7MK&_nc_gid=Tjkgx5MQrPqgeF4wnZdjLQ&edm=APNOSGoBAAAA&ccb=7-5&ig_cache_key=MzcyMTU3MjQ3MjMzNzg0OTcyNA%3D%3D.3-ccb7-5&oh=00_AfZpKwTJZoKSdFcmX4WenWDEMUceHCydZo5v5GFyrH8Hcg&oe=68CCC2FD&_nc_sid=ca40e6",
                "height": 600,
                "width": 480,
            },
            {
                "url": "https://scontent-iad3-2.cdninstagram.com/v/t51.2885-15/548964154_18527355667044533_1511165445211038365_n.jpg?stp=dst-jpg_e35_p320x320_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQuaW1hZ2VfdXJsZ2VuLjEwODB4MTM1MC5zZHIuZjgyNzg3LmRlZmF1bHRfaW1hZ2UuYzIifQ&_nc_ht=scontent-iad3-2.cdninstagram.com&_nc_cat=105&_nc_oc=Q6cZ2QFakGqpqRaqvBSF1Tf8h04TdNo057GigYrPg3CyZFDeCkj3SFTWGzxT9TMLJW7K0oI&_nc_ohc=3EuKCmVNwusQ7kNvwHLy7MK&_nc_gid=Tjkgx5MQrPqgeF4wnZdjLQ&edm=APNOSGoBAAAA&ccb=7-5&ig_cache_key=MzcyMTU3MjQ3MjMzNzg0OTcyNA%3D%3D.3-ccb7-5&oh=00_AfYyD_fj-ut32TjsxGmP8DSE2tS2snLc3fPc58Me_STfVw&oe=68CCC2FD&_nc_sid=ca40e6",
                "height": 400,
                "width": 320,
            },
            {
                "url": "https://scontent-iad3-2.cdninstagram.com/v/t51.2885-15/548964154_18527355667044533_1511165445211038365_n.jpg?stp=dst-jpg_e35_p240x240_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQuaW1hZ2VfdXJsZ2VuLjEwODB4MTM1MC5zZHIuZjgyNzg3LmRlZmF1bHRfaW1hZ2UuYzIifQ&_nc_ht=scontent-iad3-2.cdninstagram.com&_nc_cat=105&_nc_oc=Q6cZ2QFakGqpqRaqvBSF1Tf8h04TdNo057GigYrPg3CyZFDeCkj3SFTWGzxT9TMLJW7K0oI&_nc_ohc=3EuKCmVNwusQ7kNvwHLy7MK&_nc_gid=Tjkgx5MQrPqgeF4wnZdjLQ&edm=APNOSGoBAAAA&ccb=7-5&ig_cache_key=MzcyMTU3MjQ3MjMzNzg0OTcyNA%3D%3D.3-ccb7-5&oh=00_Afb8uqgWBWFSwkmtoe8Gu1vcpEJurvsGT_kuSLCHkZfsRA&oe=68CCC2FD&_nc_sid=ca40e6",
                "height": 300,
                "width": 240,
            },
            {
                "url": "https://scontent-iad3-2.cdninstagram.com/v/t51.2885-15/548964154_18527355667044533_1511165445211038365_n.jpg?stp=c0.135.1080.1080a_dst-jpg_e35_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQuaW1hZ2VfdXJsZ2VuLjEwODB4MTM1MC5zZHIuZjgyNzg3LmRlZmF1bHRfaW1hZ2UuYzIifQ&_nc_ht=scontent-iad3-2.cdninstagram.com&_nc_cat=105&_nc_oc=Q6cZ2QFakGqpqRaqvBSF1Tf8h04TdNo057GigYrPg3CyZFDeCkj3SFTWGzxT9TMLJW7K0oI&_nc_ohc=3EuKCmVNwusQ7kNvwHLy7MK&_nc_gid=Tjkgx5MQrPqgeF4wnZdjLQ&edm=APNOSGoBAAAA&ccb=7-5&ig_cache_key=MzcyMTU3MjQ3MjMzNzg0OTcyNA%3D%3D.3-ccb7-5&oh=00_Afb4WZ8gdwKVZGoBx-sK3qbdeCKpnld4WF5A5lJDn7XSAw&oe=68CCC2FD&_nc_sid=ca40e6",
                "height": 1080,
                "width": 1080,
            },
            {
                "url": "https://scontent-iad3-2.cdninstagram.com/v/t51.2885-15/548964154_18527355667044533_1511165445211038365_n.jpg?stp=c0.135.1080.1080a_dst-jpg_e35_s750x750_sh0.08_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQuaW1hZ2VfdXJsZ2VuLjEwODB4MTM1MC5zZHIuZjgyNzg3LmRlZmF1bHRfaW1hZ2UuYzIifQ&_nc_ht=scontent-iad3-2.cdninstagram.com&_nc_cat=105&_nc_oc=Q6cZ2QFakGqpqRaqvBSF1Tf8h04TdNo057GigYrPg3CyZFDeCkj3SFTWGzxT9TMLJW7K0oI&_nc_ohc=3EuKCmVNwusQ7kNvwHLy7MK&_nc_gid=Tjkgx5MQrPqgeF4wnZdjLQ&edm=APNOSGoBAAAA&ccb=7-5&ig_cache_key=MzcyMTU3MjQ3MjMzNzg0OTcyNA%3D%3D.3-ccb7-5&oh=00_AfbwRXKqVVPNIvWUVzlXHblcZ1Z9TjHsJagGrKrza-dJqg&oe=68CCC2FD&_nc_sid=ca40e6",
                "height": 750,
                "width": 750,
            },
            {
                "url": "https://scontent-iad3-2.cdninstagram.com/v/t51.2885-15/548964154_18527355667044533_1511165445211038365_n.jpg?stp=c0.135.1080.1080a_dst-jpg_e35_s640x640_sh0.08_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQuaW1hZ2VfdXJsZ2VuLjEwODB4MTM1MC5zZHIuZjgyNzg3LmRlZmF1bHRfaW1hZ2UuYzIifQ&_nc_ht=scontent-iad3-2.cdninstagram.com&_nc_cat=105&_nc_oc=Q6cZ2QFakGqpqRaqvBSF1Tf8h04TdNo057GigYrPg3CyZFDeCkj3SFTWGzxT9TMLJW7K0oI&_nc_ohc=3EuKCmVNwusQ7kNvwHLy7MK&_nc_gid=Tjkgx5MQrPqgeF4wnZdjLQ&edm=APNOSGoBAAAA&ccb=7-5&ig_cache_key=MzcyMTU3MjQ3MjMzNzg0OTcyNA%3D%3D.3-ccb7-5&oh=00_AfacizXUguBl4TakHLzbMBzQt-N3jAZcoQArbJ0OCwgnpA&oe=68CCC2FD&_nc_sid=ca40e6",
                "height": 640,
                "width": 640,
            },
            {
                "url": "https://scontent-iad3-2.cdninstagram.com/v/t51.2885-15/548964154_18527355667044533_1511165445211038365_n.jpg?stp=c0.135.1080.1080a_dst-jpg_e35_s480x480_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQuaW1hZ2VfdXJsZ2VuLjEwODB4MTM1MC5zZHIuZjgyNzg3LmRlZmF1bHRfaW1hZ2UuYzIifQ&_nc_ht=scontent-iad3-2.cdninstagram.com&_nc_cat=105&_nc_oc=Q6cZ2QFakGqpqRaqvBSF1Tf8h04TdNo057GigYrPg3CyZFDeCkj3SFTWGzxT9TMLJW7K0oI&_nc_ohc=3EuKCmVNwusQ7kNvwHLy7MK&_nc_gid=Tjkgx5MQrPqgeF4wnZdjLQ&edm=APNOSGoBAAAA&ccb=7-5&ig_cache_key=MzcyMTU3MjQ3MjMzNzg0OTcyNA%3D%3D.3-ccb7-5&oh=00_Afarnaf2WZ28614gEuXIED0jxVASNQBdFeQhe-EFizHjLg&oe=68CCC2FD&_nc_sid=ca40e6",
                "height": 480,
                "width": 480,
            },
            {
                "url": "https://scontent-iad3-2.cdninstagram.com/v/t51.2885-15/548964154_18527355667044533_1511165445211038365_n.jpg?stp=c0.135.1080.1080a_dst-jpg_e35_s320x320_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQuaW1hZ2VfdXJsZ2VuLjEwODB4MTM1MC5zZHIuZjgyNzg3LmRlZmF1bHRfaW1hZ2UuYzIifQ&_nc_ht=scontent-iad3-2.cdninstagram.com&_nc_cat=105&_nc_oc=Q6cZ2QFakGqpqRaqvBSF1Tf8h04TdNo057GigYrPg3CyZFDeCkj3SFTWGzxT9TMLJW7K0oI&_nc_ohc=3EuKCmVNwusQ7kNvwHLy7MK&_nc_gid=Tjkgx5MQrPqgeF4wnZdjLQ&edm=APNOSGoBAAAA&ccb=7-5&ig_cache_key=MzcyMTU3MjQ3MjMzNzg0OTcyNA%3D%3D.3-ccb7-5&oh=00_AfZSnYlwW9eiy-wNqW1OQCSOWPkjOzjGdG5SbmDYKIEjfg&oe=68CCC2FD&_nc_sid=ca40e6",
                "height": 320,
                "width": 320,
            },
            {
                "url": "https://scontent-iad3-2.cdninstagram.com/v/t51.2885-15/548964154_18527355667044533_1511165445211038365_n.jpg?stp=c0.135.1080.1080a_dst-jpg_e35_s240x240_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQuaW1hZ2VfdXJsZ2VuLjEwODB4MTM1MC5zZHIuZjgyNzg3LmRlZmF1bHRfaW1hZ2UuYzIifQ&_nc_ht=scontent-iad3-2.cdninstagram.com&_nc_cat=105&_nc_oc=Q6cZ2QFakGqpqRaqvBSF1Tf8h04TdNo057GigYrPg3CyZFDeCkj3SFTWGzxT9TMLJW7K0oI&_nc_ohc=3EuKCmVNwusQ7kNvwHLy7MK&_nc_gid=Tjkgx5MQrPqgeF4wnZdjLQ&edm=APNOSGoBAAAA&ccb=7-5&ig_cache_key=MzcyMTU3MjQ3MjMzNzg0OTcyNA%3D%3D.3-ccb7-5&oh=00_AfaUCyEsISy93BQKicIDUe2azmu57EwMKUl0HKmvm1NMUg&oe=68CCC2FD&_nc_sid=ca40e6",
                "height": 240,
                "width": 240,
            },
            {
                "url": "https://scontent-iad3-2.cdninstagram.com/v/t51.2885-15/548964154_18527355667044533_1511165445211038365_n.jpg?stp=c0.135.1080.1080a_dst-jpg_e35_s150x150_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQuaW1hZ2VfdXJsZ2VuLjEwODB4MTM1MC5zZHIuZjgyNzg3LmRlZmF1bHRfaW1hZ2UuYzIifQ&_nc_ht=scontent-iad3-2.cdninstagram.com&_nc_cat=105&_nc_oc=Q6cZ2QFakGqpqRaqvBSF1Tf8h04TdNo057GigYrPg3CyZFDeCkj3SFTWGzxT9TMLJW7K0oI&_nc_ohc=3EuKCmVNwusQ7kNvwHLy7MK&_nc_gid=Tjkgx5MQrPqgeF4wnZdjLQ&edm=APNOSGoBAAAA&ccb=7-5&ig_cache_key=MzcyMTU3MjQ3MjMzNzg0OTcyNA%3D%3D.3-ccb7-5&oh=00_AfYbXDPQzH2EiO6JNZZJmlogOBbdx_9TvkqutfaxCiY0yQ&oe=68CCC2FD&_nc_sid=ca40e6",
                "height": 150,
                "width": 150,
            },
        ]
    },
    "usertags": None,
    "taken_at": 1757866032,
    "previous_submitter": None,
    "link": None,
    "story_cta": None,
    "like_count": 1,
    "organic_tracking_token": (
        "eyJ2ZXJzaW9uIjo1LCJwYXlsb2FkIjp7ImlzX2FuYWx5dGljc190cmFja2VkIjp0cnVlLCJ1dWlkIjoiZGNiNjUzMmU2MjMyNDUxODlkMTdkN2I5ZDczY2NhOWQzNzIxNTcyNDcyMzM3ODQ5NzI0Iiwic2VydmVyX3Rva2VuIjoiMTc1Nzg2NjczNzg1MHwzNzIxNTcyNDcyMzM3ODQ5NzI0fDc2***fGQxNGZkMTg0NjU1MWNhODcyZjZlMmE2NDUxNzAwMWZkNzFlNjYxMWZmYzc5MTk5MzMxNDdmYmU3YTE5MGVkN2QifSwic2lnbmF0dXJlIjoiIn0="
    ),
    "preview": None,
    "product_type": "feed",
    "invited_coauthor_producers": [],
    "carousel_media_count": None,
    "all_previous_submitters": None,
    "coauthor_producers": [],
    "sponsor_tags": None,
    "follow_hashtag_info": None,
    "is_paid_partnership": False,
    "affiliate_info": None,
    "clips_attribution_info": None,
    "clips_metadata": None,
    "location": None,
    "wearable_attribution_info": None,
    "caption": (
        "\ud83d\udea3\u200d\u2640\ufe0f Come find us at the Clubs Fair! \ud83d\udc09\u2728\n"
        "Looking for a fun way to get active and meet new people? Dragon Boat might be the perfect fit. \n"
        "If you missed us at the Athletics Fair, here\u2019s your chance to meet the team!\n"
        "\ud83d\udccd SLC\n \ud83d\uddd3\ufe0f Sept 18 | 11 AM \u2013 3 PM\n "
        "\ud83d\uddd3\ufe0f Sept 19 | 11 AM \u2013 2 PM\n"
        "Stop by our booth to learn more and see how YOU can be part of the team \ud83d\udcaa"
    ),
    "caption_is_edited": False,
    "headline": None,
    "comment_count": 0,
    "comments": None,
    "view_count": None,
    "top_likers": [],
    "facepile_top_likers": [],
    "hidden_likes_string_variant": -1,
    "fb_like_count": None,
    "like_and_view_counts_disabled": False,
    "crosspost_metadata": {"is_feedback_aggregated": None},
    "social_context": [],
    "comments_disabled": None,
    "can_viewer_reshare": True,
    "can_reshare": None,
    "saved_collection_ids": None,
    "has_viewer_saved": None,
    "sharing_friction_info": {
        "should_have_sharing_friction": False,
        "bloks_app_url": None,
    },
    "commenting_disabled_for_viewer": None,
    "boosted_status": None,
    "boost_unavailable_identifier": None,
    "boost_unavailable_reason": None,
    "can_see_insights_as_brand": False,
    "ig_media_sharing_disabled": False,
    "feed_demotion_control": None,
    "feed_recs_demotion_control": None,
    "has_audio": None,
}

image_url = "https://bug-free-octo-spork.s3.us-east-2.amazonaws.com/events/a0e6f8eb-a8bf-4463-96a7-a4d388755d9e.jpg"

# Test AI client
result = extract_events_from_caption(post["caption"], image_url)
