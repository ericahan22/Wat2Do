import argparse
import asyncio
import csv
import json
import os
import sys
from datetime import datetime, timezone as dt_timezone
from pathlib import Path

# 1. Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.utils import timezone

from scraping.event_processor import EventProcessor
from scraping.instagram_scraper import InstagramScraper
from scraping.logging_config import logger

ALL_URLS = ['uwindustry4.0', 'uw.cki', 'uwaterloofec', 'wloofigureskatingclub', 'christiansonuwcampus', 'uwrgclub', 'uwma.lumsa', 'sjumusicals', 'wloofloorball', 'waterloohinduyuva', 'figmaatwaterloo', 'hopeless.hitters.academy', 'uwcubingclub', 'uw.naygn', 'uwceages', 'uw.ite.sc', 'uwrealitylabs', 'wusathrift', 'occuw', 'uwicsn', 'uwglow', 'ostem_uwaterloo', 'uwentsoc', 'uwwomenscentre', 'womeninhealthcareuw', 'infullcolouracappella', 'bigspoonlilspoon.uw', 'aiesecinwaterloo', 'asa_uwaterloo', 'uworbital', 'uwcomedy', 'waterlooblockchain', 'uwaterloowif', 'uwcancerfoundation', 'tcfwaterloo', 'psuwaterloo', 'uwewb', 'uwglobaldentalbrigades', 'uwmetal', 'uwfintech', 'wlooquantclub', 'claudeuwaterloo', 'uwpreoptclub', 'uw_predental', 'uwaterlooufo', 'uw.uxrhub', 'uw_origami', 'uwsrfss', 'uwcms.soc', 'uwaterloobyc', 'hosauwaterloo', 'uw.movie.watchers.club', 'camskids_waterloo', 'uwufurs', 'uw.kcg', 'kwcommunists', 'uw_yaf', 'soch_uwaterloo', 'uw_hope', 'uwprepharmacy', 'uwbioethics', 'uw.conservatives', 'uwglobalphbrigades', 'uwmates', 'uwdiabetesassociation', 'uwsoccerwpclub', 'jianyidance', 'waterboysuw', 'uwhealthcaresymposium', 'thewomensnetwork_waterloo', 'uwrehabsci', 'mns.soc', 'uw_bmsa', 'uwsbsa', 'uw_phys_club', 'watrox1017', 'uwchemclub', 'uwbiochem', 'uwaterloowim', 'uwmathnews', 'uwmef', 'uwpmclub', 'uw.farmsa', 'uwactsciclub', 'uwaterloosc', 'uwcsclub', 'uwmathsoc', 'waterlooenbus', 'envwags', 'uwaterloopsa', 'uwerssa', 'uw_aises', 'nsbe.waterloo', 'uwengiqueers', 'doubledegreeclub', 'fass.theatre.company', 'uw.tsu', 'uwsoc', 'uw_sofa', 'uw_psychsoc', 'uw.pssa', 'uwphilsoc', 'pacs.society', 'uwlegalstudiessociety', 'uwhrsociety', 'uwhistory', 'gbdasoc', 'uw_gsjs', 'uwcerclefrancais', 'uwenglishsociety', 'uweconsoc', 'uw.cas', 'arbussociety', 'uwanthsoc', 'uwafsa', 'uw_asu', 'ahsum.waterloo', 'uwaterloogg', 'uwstrengthclub', 'wlooclimbingclub', 'uwaterloojuggling', 'wloorunning', 'uwaterloocycling', 'wloo.archery', 'wloo.outersclub', 'wloocurling', 'uwaterloodance', 'uwballroom', 'wlooserve', 'wlootennis', 'uwaterloottc', 'wloopickleballclub', 'wloobadmintonclub', 'wloowrestling', 'uwtaekwondoacademy', 'uwmuaythai', 'wlookendo', 'wlookarate', 'wloojudo', 'wloofencing', 'wloochinesemartialarts', 'wloo_underwaterhockey', 'wlootriclub', 'wloo.lifesaving', 'wloo.dboat', 'wlooartisticswimming', 'neurodivers_uw', 'wlooband', 'uwparksclub', 'uwgeospatial', 'uw.mariokart', 'eesa_uw', 'uw_kiss', 'uw_hhss', 'uw_ess', 'uwrepairclub', 'wloocricket', 'susawaterloo', 'womeninprelawuw', 'sdgimpactalliance', 'greeklifewaterloo', 'uw_base', 'waterloolaurierpunjabis', 'uwpublicspeaking', 'uw_cybersecurity_club', 'uwacechapter', 'uofwssa', 'medlife_uwaterloo', 'formulatech.hacks', 'uw.bmlt', 'uwmusoc', 'uwrelayforlife', 'uwbugs', 'uwraise', 'wasawaterloo', 'uwyoungliberals', 'climatejusticeuw', 'wataiteam', 'uwengsoc', 'uwaterloowie', 'uwblackscience', 'uwaterloodsc', 'uwscisoc', 'uw.mwa', 'uwblueprint', 'uwvelocity', 'uw.astro', 'prismcollectiv_', 'femphys', 'designwaterloo', 'uwaterloowics', 'with.respect.to.time', 'uw_osp', 'seruwaterloo', 'uwgivesblood', 'uwaterloomeditates', 'uw_cioc', 'uwtrgbookclub', 'uwcccf', 'tma.waterloo', 'waterloolaurierssa', 'cocawaterloolaurier', 'akcse_uw', 'uw.wealthmanagement', 'uwatna', 'uwyugioh', 'uwwistem', 'uw_watsam', 'waterloosnowco', 'uwatsfic', 'wreaclub', 'uwquantum', 'waterloolaadliyan', 'uwhockeyclub', 'waterboo_uw', 'uwvfp', 'uwvisualartsclub', 'uwneuro', 'uwbeautyclub', 'uwzoologyclub', 'uwskate', 'uwaterloondp', 'uwmoot', 'uwaterloo_ksa', 'uw_jsa', 'uw.fsa', 'uw.entomology', 'uwcag', 'uwaterloobhangra', 'uwapc', 'unicefuwaterloo', 'uwchaiandverse', 'uwvsa', 'uwtss', 'uwbobatime', 'uw_ux', 'uwtetris', 'uwsupportingsickkids', 'uwstreetdance', 'uwaterloostemcellclub', 'uwsewciety', 'uwscrabble', 'uwquizbowl', 'uwaterloopremed', 'uwpokerclub', 'uwpersiansa', 'uwoperationsmile', 'uw.mehfil', 'uwmccf', 'uwkpopclub', 'uwempowercycle', 'uw.dhamaka', 'waterloocubansalsaclub', 'knituw', 'cagh_uw', 'uwbuilders', 'uwboardgames', 'uwtsa', 'uw.unaccompaniedminors', 'iicuwaterloo', 'uwacabellas', 'techplusuw', 'uw__tsa', 'uwteaclub', 'letstockaboutit', 'uwserbianstudentassociation', 'uwsmileclub', 'uw.rsa', 'uwriichi_mahjong', 'uwaterloopm', 'p2cwaterloo', 'polishsocietyuw', 'uw_pokemon_club', 'uwphotographyclub', 'uw.psa', 'onestepatatime.uw', 'nasawaterloo', 'uwaterloonsa', 'uwmsa', 'themusicalinterdudes', 'uwmun', 'uwaterloomocktrial', 'uw.marketing', 'uwmcc', 'uwmambo', 'uwmssa', 'uwmakeawishcanada', 'uwlawbusinessnexus', 'uw.lasa', 'kcfwaterloo', 'kc_waterloo', 'jamnetwork_uw', 'isaw.ca', 'uwindianca', 'uwimprovisation', 'uw_hydroponics', 'uwhvz', 'uwaterloohksa', 'uwhiphop', 'uw.hsc', 'hillelwaterloolaurier', 'itshera.co', 'hcwaterloo', 'hanvoicewaterloo', 'uw.gsa', 'uwglobalmedicalbrigades', 'globalbusinessbrigadesuw', 'uwgamedev', 'uwfinance', 'uwfilmclub_', 'fashionforchange', 'esawaterloo', 'uwdeception', 'uwdebate', 'uwaterloodj', 'uwclecwaterloo', 'uwcreatorscollective', 'uwcreativewriting', 'uw.crafts4charity', 'uwcookingclub', 'uwconcertbandclub', 'ctrla.uw', 'uwcsa', 'uwccf', 'uw.chess.club', 'uwcarivybz', 'uwcheeseclub', 'uwcampuscompost', 'cabsuw', 'uw.cube', 'uw_breakers', 'uw_aviation', 'uwaterlooacs', 'ascenduw', 'uw_animusic', 'uwanimalrights', 'aihumanrights.uw', '_afroxdance_', '_uwasa', 'uw_ace', 'uwacc', 'yourwusa']

def filter_valid_posts(posts):
    return [
        post
        for post in posts
        if not post.get("error")
        and not post.get("errorDescription")
        and post.get("url")
        and "/p/" in post.get("url")
    ]

def main():
    parser = argparse.ArgumentParser(description="Run Big Scrape")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (1 account only)")
    parser.add_argument("--limit", type=int, default=100, help="Max posts per user to scrape")
    args = parser.parse_args()

    targets = list(set(ALL_URLS))
    
    if args.dry_run:
        targets = targets[:1]
        logger.info(f"--- Big Scrape Workflow Started: {len(targets)} targets (DRY RUN) ---")
    else:
        logger.info(f"--- Big Scrape Workflow Started: {len(targets)} targets (FULL SCRAPE) ---")

    scraper = InstagramScraper()
    processor = EventProcessor(concurrency=5, big_scrape=True, dry_run=args.dry_run)

    # Scrape since Sep 1, 2025
    sep_1 = datetime(2025, 9, 1, tzinfo=dt_timezone.utc)
    now = datetime.now(dt_timezone.utc)
    days_diff = (now - sep_1).days + 1    
    logger.info(f"Scraping with cutoff_days={days_diff} (since {sep_1.date()})")

    # Batch scrape
    posts = scraper.scrape(targets, results_limit=args.limit, cutoff_days=days_diff)
    
    raw_path = Path(__file__).parent / "apify_raw_results.json"
    with raw_path.open("w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    posts = filter_valid_posts(posts)
    if not posts:
        logger.info("No posts retrieved. Exiting.")
        sys.exit(0)

    try:
        saved_count = asyncio.run(processor.process(posts, sep_1))
        logger.info(f"Successfully processed {saved_count} events")
    except Exception as e:
        logger.error(f"Critical error in processing: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
