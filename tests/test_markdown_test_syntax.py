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
        self.verify_scope('[BCE]', 'markup.italic')
        self.verify_scope(r'[\*_]', 'punctuation.definition')
        self.verify_default('[AD ]')

    def test_bold(self):
        self.set_text('''
A **B** __C__ D
**E**
''')
        self.verify_scope('[BCE]', 'markup.bold')
        self.verify_scope(r'[\*_]', 'punctuation.definition')
        self.verify_default('[AD ]')

    def test_inline_markup_inside_inline_markup(self):
        self.set_text('''
A *B **C** D* E
F **G *H* I** J
''')
        self.verify_scope('[BCDH]', 'markup.italic')
        self.verify_scope('[CGHI]', 'markup.bold')
        self.verify_scope(r'\*', 'punctuation.definition')
        self.verify_default('[AEFJ]')

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
        self.verify_scope('[BCDEF]', 'markup.italic')
        self.verify_scope('[LMNOP]', 'markup.bold')
        self.verify_scope(r'\*', 'punctuation.definition')
        self.verify_default(r'[AGKQ:;,\.?]')

    def test_inline_markup_inside_quotes_and_brackets(self):
        self.set_text('''
A "*B*" (*C*) '*D*' E
K "**L**" (**M**) '**N**' O
''')
        self.verify_scope('[BCD]', 'markup.italic')
        self.verify_scope('[LMN]', 'markup.bold')
        self.verify_scope(r'\*', 'punctuation.definition')
        self.verify_default(r'''[AEKQ"\(\)'\.]''')

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
        self.verify_default('[ACE ]')

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
        self.verify_scope('[ABCDEFKLMN]', 'entity.name.section')
        self.verify_scope('[ABCDEFKLMN# ]', 'markup.heading')
        self.verify_scope(r'#', 'punctuation.definition')
        self.verify_default(r'[GO]')

    def test_inline_markup_inside_headings(self):
        self.set_text('''
#_A_
## B _C_
### D _E_ F
#### K _L M_ N #
Z
''')
        self.verify_scope('[ABCDEFKLMN_]', 'entity.name.section')
        self.verify_scope('[ABCDEFKLMN# ]', 'markup.heading')
        self.verify_scope('[ACELM]', 'markup.italic')
        self.verify_scope(r'#', 'punctuation.definition')
        self.verify_default(r'Z')

