"""Structural and DOM-behavior checks; not a browser rendering test."""
import json
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import unittest

ASSET = Path(__file__).resolve().parents[1] / 'assets/citation-audit-template.html'


class Template(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.links, self.records, self.scripts = [], [], [], []
        self.in_script = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.append(a['id'])
        if tag == 'a':
            self.links.append(a['href'])
        if tag == 'article' and 'record' in a.get('class', '').split():
            self.records.append(a)
        if tag == 'script':
            assert 'src' not in a
            self.in_script = True

    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_script = False

    def handle_data(self, data):
        if self.in_script:
            self.scripts.append(data)


class ReportTemplateTests(unittest.TestCase):
    def setUp(self):
        self.page = Template()
        self.page.feed(ASSET.read_text())

    def test_ids_links_and_record_contract(self):
        p = self.page
        self.assertEqual(len(p.ids), len(set(p.ids)))
        for href in p.links:
            self.assertTrue(href.startswith('#'))
            self.assertIn(href[1:], p.ids)
        statuses = {'directly_supported', 'qualified', 'contradicted', 'unverified'}
        self.assertEqual({r['data-status'] for r in p.records}, statuses)
        for r in p.records:
            self.assertIn(r['data-severity'], {'none', 'informational', 'low', 'medium', 'high'})
            self.assertEqual(r['data-status'] == 'unverified', r['data-gap'] in {'access', 'support'})
        self.assertNotIn('innerHTML', ''.join(p.scripts))

    @unittest.skipUnless(shutil.which('node'), 'Node is optional; needed for DOM behavior checks')
    def test_filter_counts_and_jump_behavior(self):
        fixture = json.dumps(self.page.records)
        harness = r'''
const assert = require('node:assert/strict');
const vm = require('node:vm');
function el(id){return {id,value:'all',hidden:false,open:false,children:[],listeners:{},
 textContent:'',tagName:'DIV',parentElement:null,
 addEventListener(n,fn){this.listeners[n]=fn;},
 append(x){this.children.push(x);},replaceChildren(){this.children=[];},scrollIntoView(){this.scrolled=true;}};}
const ids={};
for(const id of ['language','query','status','severity','category','gap','totals','severity-totals','visible','info-count','information-group','attention-group','reset'])ids[id]=el(id);
ids.query.value='';ids['information-group'].tagName='DETAILS';
const raw=RECORDS;
const cards=raw.map(r=>{
 const c=el(r.id);c.dataset={};
 for(const [k,v] of Object.entries(r))if(k.startsWith('data-'))c.dataset[k.slice(5)]=v;
 c.textContent=r.id+' synthetic prose '+(r.id==='C0005'?'Directly supported':'');c.classList={contains:x=>x==='record'};
 c.parentElement=c.dataset.status==='directly_supported'?ids['information-group']:ids['attention-group'];
 c.closest=selector=>selector==='#information-group'&&c.parentElement===ids['information-group']?c.parentElement:null;
 ids[c.id]=c;return c;
});
const link=el('link');link.hash='#C0005';
const translatedNode={nodeValue:'Directly supported',parentElement:{closest(){return null;}}};
const document={documentElement:{lang:'en'},createTreeWalker(){let done=false;return {currentNode:null,nextNode(){if(done)return false;done=true;this.currentNode=translatedNode;return true;}};},getElementById:id=>ids[id],createElement:tag=>el(tag),
 querySelectorAll:sel=>sel==='.record'?cards:sel==='.record-link'?[link]:sel==='details'?[ids['information-group']]:[]};
const window={location:{hash:''},listeners:{},addEventListener(n,fn){this.listeners[n]=fn;}};
vm.runInNewContext(SCRIPT,{document,window,NodeFilter:{SHOW_TEXT:4}});
assert.match(ids['severity-totals'].textContent,/No issue \/ information 1/);
assert.match(ids['severity-totals'].textContent,/Low 2/);
assert.match(ids['severity-totals'].textContent,/Medium 2/);
assert.equal(ids.totals.children.length,4);
ids.language.value='zh';ids.language.listeners.change();
assert.equal(document.documentElement.lang,'zh-CN');assert.equal(translatedNode.nodeValue,'直接支持');
assert.match(ids['severity-totals'].textContent,/无问题／信息记录 1/);
assert.equal(ids.totals.children.length,4);
ids.query.value='直接支持';ids.query.listeners.input();assert.deepEqual(cards.filter(c=>!c.hidden).map(c=>c.id),['C0005']);
ids.language.value='en';ids.language.listeners.change();
assert.equal(translatedNode.nodeValue,'Directly supported');assert.equal(ids.query.value,'直接支持');
assert.deepEqual(cards.filter(c=>!c.hidden).map(c=>c.id),['C0005']);
ids.reset.listeners.click();
assert.equal(ids['information-group'].open,false);
ids.status.value='issues';ids.status.listeners.change();assert.equal(cards.filter(c=>!c.hidden).length,4);
ids.category.value='vision';ids.severity.value='medium';ids.category.listeners.change();
assert.deepEqual(cards.filter(c=>!c.hidden).map(c=>c.id),['C0001']);
ids.gap.value='access';ids.gap.listeners.change();assert.equal(cards.filter(c=>!c.hidden).length,0);
link.listeners.click();assert.equal(cards.filter(c=>!c.hidden).length,5);
assert.equal(ids['information-group'].open,true);assert.equal(ids.C0005.scrolled,true);
ids.reset.listeners.click();ids.category.value='text';ids.category.listeners.change();
assert.deepEqual(cards.filter(c=>!c.hidden).map(c=>c.id),['C0003','C0004','C0005']);
ids.query.value='missing phrase';ids.query.listeners.input();assert.equal(cards.filter(c=>!c.hidden).length,0);
window.location.hash='#C0002';window.listeners.hashchange();assert.equal(ids.C0002.scrolled,true);
ids['information-group'].open=false;window.listeners.beforeprint();assert.equal(ids['information-group'].open,true);
window.listeners.afterprint();assert.equal(ids['information-group'].open,false);
'''
        harness = harness.replace('RECORDS', fixture).replace('SCRIPT', json.dumps(''.join(self.page.scripts)))
        result = subprocess.run(['node', '-e', harness], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
