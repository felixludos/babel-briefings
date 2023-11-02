import omnifig as fig


@fig.script('nnn', description='Update No-Nonsense-News for today')
def update_nnn(A):

	resume = A.pull('resume', False, silent=True)

	if not resume:

		print('--- Scraping news articles ---')
		fig.run('scrape-news', A)
		print('--- Scraping complete ---')

		print('--- Sanitizing news articles ---')
		# fig.run('sanitize-news', A)
		fig.run('nlp-news', A)
		print('--- Sanitizing complete ---')

	present_script = A.pull('present_script', 'present-notion', silent=True)
	print('--- Presenting news articles ---')
	fig.run(present_script, A)
	print('--- Presenting complete ---')


	print('\nHeadlines for ready for viewing.')







