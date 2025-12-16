def merge_requirements(file1, file2, output_file):
    requirements = set()
    for fname in (file1, file2):
        with open(fname, encoding='utf-16') as infile:
            for line in infile:
                requirements.add(line.strip())
    
    with open(output_file, 'w') as outfile:
        for requirement in sorted(requirements):
            outfile.write(requirement + '\n')

merge_requirements('scrapers/requirements.txt', 'backend/requirements.txt', 'merged_requirements.txt')
