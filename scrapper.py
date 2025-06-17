def scrape_product_highlight(driver):
    # Locating the Product highlights texts
    highlights = driver.find_elements("//div[@class='pdpHighlightFullBox']/ul/li")
    highlight_text = []
    for highlight in highlights:
        highlight_text.append(highlight.getText())
    return highlight_text
