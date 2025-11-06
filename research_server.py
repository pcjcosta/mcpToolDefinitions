# Databricks notebook source
# MAGIC %%writefile mcp_project/research_server.py
# MAGIC 
# MAGIC import arxiv
# MAGIC import json
# MAGIC import os
# MAGIC from typing import List
# MAGIC from mcp.server.fastmcp import FastMCP
# MAGIC 
# MAGIC 
# MAGIC PAPER_DIR = "papers"
# MAGIC 
# MAGIC # Initialize FastMCP server
# MAGIC mcp = FastMCP("research")
# MAGIC 
# MAGIC @mcp.tool()
# MAGIC def search_papers(topic: str, max_results: int = 5) -> List[str]:
# MAGIC     """
# MAGIC     Search for papers on arXiv based on a topic and store their information.
# MAGIC     
# MAGIC     Args:
# MAGIC         topic: The topic to search for
# MAGIC         max_results: Maximum number of results to retrieve (default: 5)
# MAGIC         
# MAGIC     Returns:
# MAGIC         List of paper IDs found in the search
# MAGIC     """
# MAGIC     
# MAGIC     # Use arxiv to find the papers 
# MAGIC     client = arxiv.Client()
# MAGIC 
# MAGIC     # Search for the most relevant articles matching the queried topic
# MAGIC     search = arxiv.Search(
# MAGIC         query = topic,
# MAGIC         max_results = max_results,
# MAGIC         sort_by = arxiv.SortCriterion.Relevance
# MAGIC     )
# MAGIC 
# MAGIC     papers = client.results(search)
# MAGIC     
# MAGIC     # Create directory for this topic
# MAGIC     path = os.path.join(PAPER_DIR, topic.lower().replace(" ", "_"))
# MAGIC     os.makedirs(path, exist_ok=True)
# MAGIC     
# MAGIC     file_path = os.path.join(path, "papers_info.json")
# MAGIC 
# MAGIC     # Try to load existing papers info
# MAGIC     try:
# MAGIC         with open(file_path, "r") as json_file:
# MAGIC             papers_info = json.load(json_file)
# MAGIC     except (FileNotFoundError, json.JSONDecodeError):
# MAGIC         papers_info = {}
# MAGIC 
# MAGIC     # Process each paper and add to papers_info  
# MAGIC     paper_ids = []
# MAGIC     for paper in papers:
# MAGIC         paper_ids.append(paper.get_short_id())
# MAGIC         paper_info = {
# MAGIC             'title': paper.title,
# MAGIC             'authors': [author.name for author in paper.authors],
# MAGIC             'summary': paper.summary,
# MAGIC             'pdf_url': paper.pdf_url,
# MAGIC             'published': str(paper.published.date())
# MAGIC         }
# MAGIC         papers_info[paper.get_short_id()] = paper_info
# MAGIC     
# MAGIC     # Save updated papers_info to json file
# MAGIC     with open(file_path, "w") as json_file:
# MAGIC         json.dump(papers_info, json_file, indent=2)
# MAGIC     
# MAGIC     print(f"Results are saved in: {file_path}")
# MAGIC     
# MAGIC     return paper_ids
# MAGIC 
# MAGIC @mcp.tool()
# MAGIC def extract_info(paper_id: str) -> str:
# MAGIC     """
# MAGIC     Search for information about a specific paper across all topic directories.
# MAGIC     
# MAGIC     Args:
# MAGIC         paper_id: The ID of the paper to look for
# MAGIC         
# MAGIC     Returns:
# MAGIC         JSON string with paper information if found, error message if not found
# MAGIC     """
# MAGIC  
# MAGIC     for item in os.listdir(PAPER_DIR):
# MAGIC         item_path = os.path.join(PAPER_DIR, item)
# MAGIC         if os.path.isdir(item_path):
# MAGIC             file_path = os.path.join(item_path, "papers_info.json")
# MAGIC             if os.path.isfile(file_path):
# MAGIC                 try:
# MAGIC                     with open(file_path, "r") as json_file:
# MAGIC                         papers_info = json.load(json_file)
# MAGIC                         if paper_id in papers_info:
# MAGIC                             return json.dumps(papers_info[paper_id], indent=2)
# MAGIC                 except (FileNotFoundError, json.JSONDecodeError) as e:
# MAGIC                     print(f"Error reading {file_path}: {str(e)}")
# MAGIC                     continue
# MAGIC     
# MAGIC     return f"There's no saved information related to paper {paper_id}."
# MAGIC 
# MAGIC 
# MAGIC 
# MAGIC if __name__ == "__main__":
# MAGIC     # Initialize and run the server
# MAGIC     mcp.run(transport='stdio')