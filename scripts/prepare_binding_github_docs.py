#!/usr/bin/env python3
"""Create a repository-relative master document without editing frozen reports."""
import csv
import os
from pathlib import Path
import re
import urllib.parse

ROOT=Path(__file__).resolve().parents[1]


def main():
    source=ROOT/'reports/binding/master_research_report_v3.md'
    destination=ROOT/'docs/binding/MASTER_REPORT.md'
    with (ROOT/'reproducibility/compressed_artifacts.csv').open() as stream:
        compressed={row['original_path']:row['stored_path'] for row in csv.DictReader(stream)}
    replaced=0
    def link(match):
        nonlocal replaced
        label,url=match.groups();parts=urllib.parse.urlsplit(url)
        if parts.scheme or url.startswith('#'):return match[0]
        original=(source.parent/urllib.parse.unquote(parts.path)).resolve()
        if original==ROOT.parent/'dependvar.txt':target=ROOT/'docs/binding/dependvar_20261025.txt'
        elif original.is_relative_to(ROOT):
            relative=str(original.relative_to(ROOT))
            target=ROOT/compressed.get(relative,relative)
            if relative in compressed:replaced+=1
        else:raise ValueError('Unexpected outside-repository document link: '+url)
        if not target.exists():raise ValueError('Missing publication link: '+str(target))
        relative=os.path.relpath(target,destination.parent)
        if parts.fragment:relative+='#'+parts.fragment
        return f'{label}({relative})'
    body=re.sub(r'(!?\[[^\]]*\])\(([^)]+)\)',link,source.read_text())
    introduction='''> **GitHub edition.** This is the repository-relative edition of the October 29 master report. All scientific results are unchanged. For the interactive walkthrough, download the [self-contained HTML edition](../../reports/binding/master_research_report_v3.html) and open it in a browser. Large evidence files are losslessly compressed; see the [artifact catalog and restore commands](../../reproducibility/README.md). The [original plan](dependvar_20261025.txt) is included in this repository.\n\n'''
    first,rest=body.split('\n\n',1);destination.write_text(first+'\n\n'+introduction+rest)
    for path in [ROOT/'README.md',ROOT/'reports/binding/README.md',ROOT/'reports/binding/implementation_checklist.md',ROOT/'reports/binding/research_backlog.md']:
        text=path.read_text()
        if '**Start here: [Master research report' not in text:continue
        target=os.path.relpath(destination,path.parent)
        text=re.sub(r'(\*\*Start here: \[Master research report[^\]]*\]\()[^)]*(\)\*\*)',lambda m:m[1]+target+m[2],text,count=1)
        path.write_text(text)
    index=ROOT/'reports/binding/MASTER_REPORT.md'
    text=index.read_text()
    if 'GitHub-friendly master document' not in text:
        title,rest=text.split('\n\n',1);index.write_text(title+'\n\n[GitHub-friendly master document](../../docs/binding/MASTER_REPORT.md)\n\n'+rest)
    print(f'Prepared portable master report; {replaced} large-evidence links mapped to compressed storage.')


if __name__=='__main__':main()
