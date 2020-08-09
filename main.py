
import omnifig as fig

import src



@fig.Script('nnn', description='Update No-Nonsense-News for today')
def update_nnn(A):
	
	resume = A.pull('resume', False, silent=True)
	
	if not resume:
	
		print('--- Scraping news articles ---')
		fig.run('scrape-news', A)
		print('--- Scraping complete ---')
		
		print('--- Sanitizing news articles ---')
		fig.run('sanitize-news', A)
		print('--- Sanitizing complete ---')
	
	present_script = A.pull('present_script', 'present-notion', silent=True)
	print('--- Presenting news articles ---')
	fig.run(present_script, A)
	print('--- Presenting complete ---')
	

	print('\nHeadlines for ready for viewing.')
	

if __name__ == '__main__':
	fig.entry('nnn')
