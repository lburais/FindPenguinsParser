from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

# Input / output filenames
INPUT_HTML = "pages/franklin-ii.html"   # put your downloaded HTML here
OUTPUT_XML = "pages/profile_franklin_ii.xml"


def extract_profile_to_xml(html_path, xml_path):
    # Read HTML file
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # ------- User box -------
    user_box = soup.find("div", class_="userBox")
    if not user_box:
        raise RuntimeError("userBox not found in HTML")

    # Name in nameBox
    name_el = user_box.select_one(".nameBox h1 a")
    name = name_el.get_text(strip=True) if name_el else ""

    # Details in detailBox (bio, location, website)
    bio_el = user_box.select_one(".detailBox #clampedBox span")
    bio = bio_el.get_text(strip=True) if bio_el else ""

    # Location link inside extras
    loc_el = user_box.select_one(".detailBox .extras a[href*='explore?q=']")
    location = loc_el.get_text(strip=True) if loc_el else ""

    # Website inside extras
    web_el = user_box.select_one(".detailBox .extras a.website")
    website = web_el["href"] if web_el and web_el.has_attr("href") else ""

    # Picture in pictureBox
    pic_el = user_box.select_one(".pictureBox .pp img")
    picture = pic_el["src"] if pic_el and pic_el.has_attr("src") else ""

    # ------- Trips list -------
    trips = []
    for box in soup.select(".tripList .box"):
        # Link of the trip preview
        link_el = box.select_one("a.trip-preview")
        link = link_el["href"] if link_el and link_el.has_attr("href") else ""

        # Title and period
        title_el = box.select_one(".content .title h2")
        title = title_el.get_text(strip=True) if title_el else ""

        period_el = box.select_one(".content .title .subline")
        period = period_el.get_text(strip=True) if period_el else ""

        # Stats: countries, footprints, days
        stats = box.select(".content .stats li")
        countries = stats[0].b.get_text(strip=True) if len(stats) > 0 and stats[0].b else ""
        footprints = stats[1].b.get_text(strip=True) if len(stats) > 1 and stats[1].b else ""
        days = stats[2].b.get_text(strip=True) if len(stats) > 2 and stats[2].b else ""

        trips.append(
            {
                "title": title,
                "period": period,
                "countries": countries,
                "footprints": footprints,
                "days": days,
                "url": link,
            }
        )

    # ------- Build XML -------
    root = ET.Element("profile")

    user_el = ET.SubElement(root, "user")
    ET.SubElement(user_el, "name").text = name
    ET.SubElement(user_el, "bio").text = bio
    ET.SubElement(user_el, "location").text = location
    ET.SubElement(user_el, "website").text = website
    ET.SubElement(user_el, "picture").text = picture

    trips_el = ET.SubElement(root, "trips")
    for t in trips:
        trip_el = ET.SubElement(trips_el, "trip")
        for key, value in t.items():
            ET.SubElement(trip_el, key).text = value

    # Pretty print the XML (optional)
    def indent(elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            for child in elem:
                indent(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = i
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

    indent(root)

    tree = ET.ElementTree(root)
    tree.write(xml_path, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    extract_profile_to_xml(INPUT_HTML, OUTPUT_XML)
    print(f"XML written to {OUTPUT_XML}")
