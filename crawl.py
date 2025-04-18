import asyncio
import nest_asyncio
nest_asyncio.apply()
from crawl4ai import *

from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator


async def simple_crawl():
    crawler_run_config = CrawlerRunConfig( cache_mode=CacheMode.BYPASS)
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://rgs-ibg.onlinelibrary.wiley.com/doi/full/10.1002/geo2.96",
            config=crawler_run_config
        )
        print(result.markdown.raw_markdown[:500].replace("\n", " -- "))  # Print the first 500 characters

# asyncio.run(simple_crawl())   

async def crawl_dynamic_content():
    # You can use wait_for to wait for a condition to be met before returning the result
    # wait_for = """() => {
    #     return Array.from(document.querySelectorAll('article.tease-card')).length > 10;
    # }"""

    # wait_for can be also just a css selector
    # wait_for = "article.tease-card:nth-child(10)"

    async with AsyncWebCrawler() as crawler:
        js_code = [
            "const loadMoreButton = Array.from(document.querySelectorAll('button')).find(button => button.textContent.includes('Load More')); loadMoreButton && loadMoreButton.click();"
        ]
        config = CrawlerRunConfig(
            cache_mode=CacheMode.ENABLED,
            js_code=js_code,
            # wait_for=wait_for,
        )
        result = await crawler.arun(
            url="https://digitalcommons.usu.edu/smallsat/2013/all2013/120/",
            config=config,

        )
        print(result.markdown.raw_markdown[:500].replace("\n", " -- "))  # Print first 500 characters



async def clean_content():
    async with AsyncWebCrawler(verbose=True) as crawler:
        config = CrawlerRunConfig(
            cache_mode=CacheMode.ENABLED,
            excluded_tags=['nav', 'footer', 'aside'],
            remove_overlay_elements=True,
            markdown_generator=DefaultMarkdownGenerator(
                content_filter=PruningContentFilter(threshold=0.48, threshold_type="fixed", min_word_threshold=0),
                options={
                    "ignore_links": True
                }
            ),
        )
        result = await crawler.arun(
            url="https://ift.onlinelibrary.wiley.com/doi/full/10.1111/1541-4337.13069",
            config=config,
        )
        full_markdown_length = len(result.markdown.raw_markdown)
        fit_markdown_length = len(result.markdown.fit_markdown)
        print(f"Full Markdown Length: {full_markdown_length}")
        print(f"Fit Markdown Length: {fit_markdown_length}")




async def link_analysis():
    async with AsyncWebCrawler() as crawler:
        config = CrawlerRunConfig(
            cache_mode=CacheMode.ENABLED,
            exclude_external_links=True,
            exclude_social_media_links=True,
            # exclude_domains=["facebook.com", "twitter.com"]
        )
        result = await crawler.arun(
            url="https://www.sciencedirect.com/science/article/abs/pii/S0921800909002742",
            config=config,
        )
        print(f"Found {len(result.links['internal'])} internal links")
        print(f"Found {len(result.links['external'])} external links")

        for link in result.links['internal'][:5]:
            print(f"Href: {link['href']}\nText: {link['text']}\n")
            
            
async def media_handling():
    async with AsyncWebCrawler() as crawler:
        config = CrawlerRunConfig(
            cache_mode=CacheMode.ENABLED,
            exclude_external_images=False,
            # screenshot=True # Set this to True if you want to take a screenshot
        )
        result = await crawler.arun(
            url="https://rgs-ibg.onlinelibrary.wiley.com/doi/full/10.1002/geo2.96",
            config=config,
        )
        for img in result.media['images'][:5]:
            print(f"Image URL: {img['src']}, Alt: {img['alt']}, Score: {img['score']}")


async def markdown():
    config = CrawlerRunConfig(
        markdown_generator=DefaultMarkdownGenerator()
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://www.sciencedirect.com/science/article/abs/pii/S0167880912000345", config=config)

        if result.success:
            print("Raw Markdown Output:\n")
            print(result.markdown)  # The unfiltered markdown from the page
        else:
            print("Crawl failed:", result.error_message)



if __name__ == "__main__":
# #     asyncio.run(main())
#     # asyncio.run(link_analysis())
    # asyncio.run(media_handling())
#   asyncio.run(crawl_dynamic_content())
    # asyncio.run(clean_content())
    # asyncio.run(markdown())


# import os
# import asyncio
# import json
# from pydantic import BaseModel, Field
# from typing import List
# from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LLMConfig
# from crawl4ai.extraction_strategy import LLMExtractionStrategy

# class Product(BaseModel):
#     name: str
#     price: str

# async def main():
#     # 1. Define the LLM extraction strategy
#     llm_strategy = LLMExtractionStrategy(
#         llm_config = LLMConfig(provider="openai/gpt-4o-mini", api_token="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"), # api_token=os.getenv('OPENAI_API_KEY')),
#         # schema=Product.model_json_schema(), # Or use model_json_schema()
#         # extraction_type="schema",
#         instruction="Extract all informations relevant about 'coffee' 'carbon' 'footprint' from the content.",
#         chunk_token_threshold=1000,
#         overlap_rate=0.0,
#         apply_chunking=True,
#         input_format="markdown",   # or "html", "fit_markdown"
#         extra_args={"temperature": 0.0, "max_tokens": 800}
#     )

#     # 2. Build the crawler config
#     crawl_config = CrawlerRunConfig(
#         extraction_strategy=llm_strategy,
#         cache_mode=CacheMode.BYPASS
#     )

#     # 3. Create a browser config if needed
#     browser_cfg = BrowserConfig(headless=True)

#     async with AsyncWebCrawler(config=browser_cfg) as crawler:
#         # 4. Let's say we want to crawl a single page
#         result = await crawler.arun(
#             url="https://rgs-ibg.onlinelibrary.wiley.com/doi/full/10.1002/geo2.96",
#             config=crawl_config
#         )

#         if result.success:
#             # 5. The extracted content is presumably JSON
#             data = json.loads(result.extracted_content)
#             print("Extracted items:", data)

#             # 6. Show usage stats
#             llm_strategy.show_usage()  # prints token usage
#         else:
#             print("Error:", result.error_message)

# if __name__ == "__main__":
#     asyncio.run(main())