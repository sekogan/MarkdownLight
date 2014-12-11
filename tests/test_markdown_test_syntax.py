import syntax_test

class TestMarkdownTestSyntax(syntax_test.SyntaxTestCase):
    def setUp(self):
        super().setUp()
        self.set_syntax_file("Packages/MarkdownTest/MarkdownTest.tmLanguage")
        self.set_default_scope('text')

    def test_simple_text(self):
        self.set_text('A B C')
        self.verify_default('A B C')

    def test_italic(self):
        self.set_text('''
A *B* _C_ D
*E*
''')
        self.verify_scope(list('BCE'), 'markup.italic')
        self.verify_scope(r'[\*_]', 'punctuation.definition')
        self.verify_default(list('AD '))

    def test_bold(self):
        self.set_text('''
A **B** __C__ D
**E**
''')
        self.verify_scope(list('BCE'), 'markup.bold')
        self.verify_scope(r'[\*_]', 'punctuation.definition')
        self.verify_default(list('AD '))

    def test_inline_markup_inside_inline_markup(self):
        self.set_text('''
A *B **C** D* E
F **G *H* I** J
''')
        self.verify_scope(list('BCDH'), 'markup.italic')
        self.verify_scope(list('CGHI'), 'markup.bold')
        self.verify_scope(r'\*', 'punctuation.definition')
        self.verify_default(list('AEFJ'))

    def test_bold_italic(self):
        self.set_text('''
AA *__AB__* AC
BA _**BB**_ BC
CA **_CB_** CC
DA __*DB*__ DC
''')
        self.verify_scope(r'[A-Z]B', 'markup.bold')
        self.verify_scope(r'[A-Z]B', 'markup.italic')
        self.verify_scope(r'[\*_]', 'punctuation.definition')
        self.verify_default([ r'[A-Z]A ', r' [A-Z]C', ' ' ])

    def test_multiline_markup_not_supported(self):
        # Multiline markup is not supported due to
        # limitations in syntax definition language.
        self.set_text('''
A **B
C** D
E _F
G_ H
''')
        self.verify_default('.')

    def test_inline_markup_before_punctuation(self):
        self.set_text('''
A *B*: *C*; *D*, *E*. *F*? G
K **L**: **M**; **N**, **O**. **P**? Q
''')
        self.verify_scope(list('BCDEF'), 'markup.italic')
        self.verify_scope(list('LMNOP'), 'markup.bold')
        self.verify_scope(r'\*', 'punctuation.definition')
        self.verify_default(r'[AGKQ:;,\.?]')

    def test_inline_markup_inside_quotes_and_brackets(self):
        self.set_text('''
A "*B*" (*C*) '*D*' E
K "**L**" (**M**) '**N**' O
''')
        self.verify_scope(list('BCD'), 'markup.italic')
        self.verify_scope(list('LMN'), 'markup.bold')
        self.verify_scope(r'\*', 'punctuation.definition')
        self.verify_default(r'''[AEKQ"\(\)'\.]''')

    def test_brackets_inside_inline_markup(self):
        self.set_text('''
*A (B C)*: D
*(K)* **(L)**
''')
        self.verify_scope([ r'A \(B C\)', r'\(K\)' ] , 'markup.italic')
        self.verify_scope( r'\(L\)', 'markup.bold')
        self.verify_scope(r'\*', 'punctuation.definition')
        self.verify_default(r': D')

    def test_inline_markup_combinations(self):
        self.set_text('_A _ B_C D_E _ F_ *G* **H** <a>_I_</a>')
        self.verify_scope([ 'A _ B_C D_E _ F',
            'G', 'I' ], 'markup.italic')
        self.verify_scope('H', 'markup.bold')
        self.verify_default([ '<a>', '</a>' ])

    def test_escaping_of_inline_punctuation(self):
        self.set_text(r'A *\*B\** C **D\*** E')
        self.verify_scope(r'\\\*B\\\*', 'markup.italic')
        self.verify_scope(r'D\\\*', 'markup.bold')
        self.verify_default(list('ACE '))

    def test_markup_does_not_work_inside_words(self):
        self.set_text('A_B C_D_E')
        self.verify_default('.+')

    def test_headings(self):
        self.set_text('''
# A
## B
### C
#### D
##### E
###### F
G
#K
##L#
### M ##
#### N ###########
O
''')
        self.verify_scope(list('ABCDEFKLMN'), 'entity.name.section')
        self.verify_scope(list('ABCDEFKLMN# '), 'markup.heading')
        self.verify_scope(r'#', 'punctuation.definition')
        self.verify_default(list('GO'))

    def test_inline_markup_inside_headings(self):
        self.set_text('''
#_A_
## B _C_
### D _E_ F
#### K _L M_ N #
Z
''')
        self.verify_scope(list('ABCDEFKLMN_'), 'entity.name.section')
        self.verify_scope(list('ABCDEFKLMN# '), 'markup.heading')
        self.verify_scope(list('ACELM'), 'markup.italic')
        self.verify_scope(r'#', 'punctuation.definition')
        self.verify_default(r'Z')

    def test_fenced_paragraph(self):
        self.set_text('''
K

```
A
```

L
''')
        self.verify_scope('A', 'markup.raw.block.fenced')
        self.verify_scope('`', 'punctuation.definition')
        self.verify_default([ r'K\n\n', r'\nL\n' ])

    def test_fenced_block_inside_paragraph(self):
        self.set_text('''

K
```
A
```
L

''')
        self.verify_scope('A', 'markup.raw.block.fenced')
        self.verify_scope('`', 'punctuation.definition')
        self.verify_default([ r'\nK\n', r'L\n\n' ])

    def test_syntax_highlighting_inside_fenced_blocks(self):
        self.set_text('''
``` c++
int x = 123;
```
```python
def g():
    return 567
```
''')
        self.verify_scope([ 'int', 'def' ], 'storage.type')
        self.verify_scope([ '123', '567' ], 'constant.numeric')
        self.verify_scope('g', 'entity.name')
        self.verify_scope('return', 'keyword.control')

    def test_indented_raw_blocks(self):
        self.set_text('''
A

    B

C
''')
        self.verify_scope(r'    B\n', 'markup.raw.block')
        self.verify_default([ r'\nA\n\n', r'\nC\n' ])

    def test_multiline_indented_raw_blocks(self):
        self.set_text('''
    A
    B
''')
        self.verify_scope([ r'    A\n', r'    B\n' ],
            'markup.raw.block')

    def test_indented_raw_blocks_glued_to_text(self):
        self.set_text('''
A
    B

    C
D
''')
        self.verify_scope(r'    C\n', 'markup.raw.block')
        self.verify_default([ r'\nA\n    B\n\n', r'D\n' ])

    def test_blank_line_is_not_indented_raw_block(self):
        self.set_text('\n\n    \n\n')
        self.verify_default(r'\n[ ]+\n')

    def test_inline_raw_text(self):
        self.set_text('''
A `B` C
D`E`F
K `L **M` N** O
''')
        self.verify_scope(list('BE') + [ r'L \*\*M' ], 'markup.raw.inline')
        self.verify_scope('`', 'punctuation.definition')
        self.verify_default(list('ACDFK') + [ r' N\*\* O' ])

    def test_incomplete_or_multiline_inline_raw_text(self):
        self.set_text('''
A `B
C` D
''')
        self.verify_default('.+')
