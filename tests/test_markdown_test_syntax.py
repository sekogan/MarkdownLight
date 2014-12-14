import syntax_test

class TestMarkdownTestSyntax(syntax_test.SyntaxTestCase):
    def setUp(self):
        super().setUp()
        self.set_syntax_file("Packages/MarkdownTest/MarkdownTest.tmLanguage")

    def check_default(self, patterns):
        self.check_in_single_scope(patterns, 'text')

    def test_simple_text(self):
        self.set_text('A B C')
        self.check_default('A B C')

    def test_italic(self):
        self.set_text('''
A *B* _C_ D
*E*
''')
        self.check_eq_scope(list('BCE'), 'markup.italic')
        self.check_eq_scope(r'[\*_]', 'punctuation.definition')
        self.check_default(list('AD '))

    def test_bold(self):
        self.set_text('''
A **B** __C__ D
**E**
''')
        self.check_eq_scope(list('BCE'), 'markup.bold')
        self.check_eq_scope(r'[\*_]+', 'punctuation.definition')
        self.check_default(list('AD '))

    def test_inline_markup_inside_inline_markup(self):
        self.set_text('''
A *B **C** D* E
F **G *H* I** J
''')
        self.check_eq_scope(r'B \*\*C\*\* D', 'markup.italic')
        self.check_eq_scope(r'H', 'markup.italic')
        self.check_eq_scope(r'C', 'markup.bold')
        self.check_eq_scope(r'G \*H\* I', 'markup.bold')
        self.check_eq_scope(r'\*+', 'punctuation.definition')
        self.check_default(list('AEFJ'))

    def test_bold_italic(self):
        self.set_text('''
AA *__AB__* AC
BA _**BB**_ BC
CA **_CB_** CC
DA __*DB*__ DC
''')
        self.check_eq_scope(r'__AB__', 'markup.italic')
        self.check_eq_scope(r'\*\*BB\*\*', 'markup.italic')
        self.check_eq_scope([ 'CB', 'DB' ], 'markup.italic')
        self.check_eq_scope([ 'AB', 'BB' ], 'markup.bold')
        self.check_eq_scope(r'_CB_', 'markup.bold')
        self.check_eq_scope(r'\*DB\*', 'markup.bold')
        self.check_eq_scope(r'\*+|_+', 'punctuation.definition')
        self.check_default([ r'[A-Z]A ', r' [A-Z]C\n' ])

    def test_multiline_markup_not_supported(self):
        # Multiline inline markup is not supported due to
        # limitations in syntax definition language.
        self.set_text('''
A **B
C** D
E _F
G_ H
''')
        self.check_default('.+')

    def test_inline_markup_before_punctuation(self):
        self.set_text('''
A *B*: *C*; *D*, *E*. *F*? G
K **L**: **M**; **N**, **O**. **P**? Q
''')
        self.check_eq_scope(list('BCDEF'), 'markup.italic')
        self.check_eq_scope(list('LMNOP'), 'markup.bold')
        self.check_eq_scope(r'\*+', 'punctuation.definition')
        self.check_default(r'[AGKQ:;,\.?]')

    def test_inline_markup_inside_quotes_and_brackets(self):
        self.set_text('''
A "*B*" (*C*) '*D*' E
K "**L**" (**M**) '**N**' O
''')
        self.check_eq_scope(list('BCD'), 'markup.italic')
        self.check_eq_scope(list('LMN'), 'markup.bold')
        self.check_eq_scope(r'\*+', 'punctuation.definition')
        self.check_default(r'''[AEKQ"\(\)'\.]''')

    def test_brackets_inside_inline_markup(self):
        self.set_text('''
*A (B C)*: D
*(K)* **(L)**
''')
        self.check_eq_scope([ r'A \(B C\)', r'\(K\)' ] , 'markup.italic')
        self.check_eq_scope( r'\(L\)', 'markup.bold')
        self.check_eq_scope(r'\*+', 'punctuation.definition')
        self.check_default(r': D')

    def test_inline_markup_combinations(self):
        self.set_text('_A _ B_C D_E _ F_ *G* **H** <a>_I_</a>')
        self.check_eq_scope([ 'A _ B_C D_E _ F',
            'G', 'I' ], 'markup.italic')
        self.check_eq_scope('H', 'markup.bold')
        self.check_default([ '<a>', '</a>' ])

    def test_escaping_of_inline_punctuation(self):
        self.set_text(r'A *\*B\** C **D\*** E')
        self.check_eq_scope(r'\\\*B\\\*', 'markup.italic')
        self.check_eq_scope(r'D\\\*', 'markup.bold')
        self.check_default(list('ACE '))

    def test_inline_markup_does_not_work_inside_words(self):
        self.set_text('A_B C_D_E')
        self.check_default('.+')

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
        self.check_eq_scope(list('ABCDEFKLMN'), 'entity.name.section')
        self.check_in_scope(list('ABCDEFKLMN# '), 'markup.heading')
        self.check_eq_scope(r'#+', 'punctuation.definition')
        self.check_default(list('GO'))

    def test_inline_markup_inside_headings(self):
        self.set_text('''
#_A_
## B _C_
### D _E_ F
#### K _L M_ N #
Z
''')
        self.check_eq_scope([
            '_A_', 'B _C_', 'D _E_ F', 'K _L M_ N'
            ], 'entity.name.section')
        self.check_in_scope(list('ABCDEFKLMN#_ '), 'markup.heading')
        self.check_eq_scope([ 'A', 'C', 'E', 'L M' ], 'markup.italic')
        self.check_eq_scope(r'#+', 'punctuation.definition')
        self.check_default(r'Z')

    def test_fenced_paragraph(self):
        self.set_text('''
K

```
A
```

L
''')
        self.check_eq_scope(r'```\nA\n```\n', 'markup.raw.block.fenced')
        self.check_eq_scope('`+', 'punctuation.definition')
        self.check_default([ r'K\n\n', r'\nL\n' ])

    def test_fenced_block_inside_paragraph(self):
        self.set_text('''

K
```
A
```
L

''')
        self.check_eq_scope(r'```\nA\n```\n', 'markup.raw.block.fenced')
        self.check_eq_scope('`+', 'punctuation.definition')
        self.check_default([ r'\nK\n', r'L\n\n' ])

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
        self.check_eq_scope([ 'int', 'def' ], 'storage.type')
        self.check_eq_scope([ '123', '567' ], 'constant.numeric')
        self.check_eq_scope('g', 'entity.name')
        self.check_eq_scope('return', 'keyword.control')

    def test_indented_raw_blocks(self):
        self.set_text('''
A

    B

C
''')
        self.check_eq_scope(r'    B\n', 'markup.raw.block')
        self.check_default([ r'\nA\n\n', r'\nC\n' ])

    def test_multiline_indented_raw_blocks(self):
        self.set_text('''
    A
    B
''')
        self.check_eq_scope(r'    A\n    B\n', 'markup.raw.block')

    def test_indented_raw_blocks_glued_to_text(self):
        self.set_text('''
A
    B

    C
D
''')
        self.check_eq_scope(r'    C\n', 'markup.raw.block')
        self.check_default([ r'\nA\n    B\n\n', r'D\n' ])

    def test_blank_line_is_not_indented_raw_block(self):
        self.set_text('\n\n    \n\n')
        self.check_default(r'\n[ ]+\n')

    def test_inline_raw_text(self):
        self.set_text('''
A `B` C
D`E`F
K `L **M` N** O
''')
        self.check_eq_scope(list('BE') + [ r'L \*\*M' ], 'markup.raw.inline.content')
        self.check_eq_scope('`', 'punctuation.definition')
        self.check_default(list('ACDFK') + [ r' N\*\* O' ])

    def test_incomplete_or_multiline_inline_raw_text(self):
        self.set_text('''
A `B
C` D
''')
        self.check_default('.+')

    def test_multiple_backquotes_as_inline_raw_delimiters(self):
        self.set_text('''
``A``
```B``
``C```
''')
        self.check_eq_scope(list('AC'), 'markup.raw.inline.content')
        self.check_eq_scope('`B', 'markup.raw.inline.content')
        self.check_eq_scope([ r'^``', r'(?<=\w)``' ], 'punctuation.definition')
        self.check_default([ r'(?<=C``)`', r'\n' ])        

    def test_inline_raw_delimiters_does_not_start_fenced_block(self):
        self.set_text('''
```A```
B
''')
        self.check_eq_scope('```A```', 'markup.raw.inline.markdown')
        self.check_eq_scope('A', 'markup.raw.inline.content')
        self.check_eq_scope('```', 'punctuation.definition')
        self.check_default(r'B')        

    def test_quoted_text_alone(self):
        self.set_text('>A\n')
        self.check_eq_scope(r'>A\n', 'markup.quote')
        self.check_eq_scope(r'>', 'punctuation.definition')

    def test_one_line_quoted_block(self):
        self.set_text('''
>A

B
''')
        self.check_eq_scope(r'>A\n', 'markup.quote')
        self.check_eq_scope(r'>', 'punctuation.definition')
        self.check_default(r'\nB\n')

    def test_type_1_multiline_quoted_block(self):
        self.set_text('''
>A
B

C
''')
        self.check_eq_scope(r'>A\nB\n', 'markup.quote')
        self.check_eq_scope(r'>', 'punctuation.definition')
        self.check_default(r'\nC\n')

    def test_type_2_multiline_quoted_block(self):
        self.set_text('''
>A
>B

C
''')
        self.check_eq_scope(r'>A\n>B\n', 'markup.quote')
        self.check_eq_scope(r'>', 'punctuation.definition')
        self.check_default(r'\nC\n')

    def test_quoted_block_inside_paragraph(self):
        self.set_text('''
A
>B

C
''')
        self.check_eq_scope(r'>B\n', 'markup.quote')
        self.check_default([ r'\nA\n', r'\nC\n' ])

    def test_spaces_before_and_after_quote_signs(self):
        self.set_text('''
 > A
  >  B
   >   C

D
''')
        self.check_eq_scope(r' > A\n {2}> {2}B\n {3}> {3}C\n', 'markup.quote')
        self.check_eq_scope(r'>', 'punctuation.definition')
        self.check_default(r'\nD\n')

    def test_inline_markup_inside_quoted_text(self):
        self.set_text('''
> `A`
>  _B_
> **C**
''')
        self.check_eq_scope('A', 'markup.raw.inline.content')
        self.check_eq_scope('B', 'markup.italic')
        self.check_eq_scope('C', 'markup.bold')

    def test_list_item_alone(self):
        self.set_text(
'''- A
''')
        self.check_eq_scope(r'- A\n', 'meta.paragraph.list')
        self.check_eq_scope(r'-', 'punctuation.definition')

    def test_multiline_list(self):
        self.set_text('''
- A
- B

C
''')
        self.check_eq_scope(r'- A\n- B\n', 'meta.paragraph.list')
        self.check_eq_scope(r'-', 'punctuation.definition')
        self.check_default(r'\nC\n')

    def test_different_types_of_unnumbered_list_bullets(self):
        self.set_text('''
- A
+ B
* C

D
''')
        self.check_eq_scope(r'- A\n\+ B\n\* C\n', 'meta.paragraph.list')
        self.check_eq_scope([ r'\+', r'\*', '-' ], 'punctuation.definition')
        self.check_default(r'D')

    def test_numbered_list(self):
        self.set_text('''
0. A
1. B
12345. C

D
''')
        self.check_eq_scope(r'0\. A\n1\. B\n\d+\. C\n', 'meta.paragraph.list')
        self.check_eq_scope([ r'0\.', r'1\.', '12345\.' ], 'punctuation.definition')
        self.check_default(r'D')

    def test_nested_lists(self):
        self.set_text('''
- A
 * B
  + C
   1. D
2. E

Z
''')
        self.check_eq_scope(r'- A\n \* B\n  \+ C\n +1\. D\n2\. E\n', 'meta.paragraph.list')
        self.check_eq_scope([ '-', r'\*', r'\+', r'1\.', r'2\.' ], 'punctuation.definition')
        self.check_default('Z')

    def test_spaces_after_bullet(self):
        self.set_text('''
-A
- B
-    C

Z
''')
        self.check_eq_scope(r'- B\n- +C\n', 'meta.paragraph.list')
        self.check_eq_scope([ r'-(?= B)', r'-(?= +C)' ], 'punctuation.definition')
        self.check_default('Z')

    def test_list_inside_paragraph(self):
        self.set_text('''
A
- B
C
''')
        self.check_eq_scope(r'- B\n', 'meta.paragraph.list')
        self.check_default([ r'\nA\n', r'C\n' ])

    def test_inline_markup_inside_list_items(self):
        self.set_text('''
- `A`
- _B_
- **C**
''')
        self.check_in_scope(r'-.*$\n', 'meta.paragraph.list')
        self.check_eq_scope('A', 'markup.raw.inline.content')
        self.check_eq_scope('B', 'markup.italic')
        self.check_eq_scope('C', 'markup.bold')
