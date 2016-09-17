import fixture

class TestMarkdownLight(fixture.SyntaxTestCase):
    def setUp(self):
        super().setUp()
        self.set_syntax_file("Packages/MarkdownLight/MarkdownLight.tmLanguage")

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
        self.check_eq_scope([ r'\*B\*', '_C_', r'\*E\*' ], 'markup.italic')
        self.check_eq_scope(r'[\*_]', 'punctuation.definition')
        self.check_default(list('AD '))

    def test_bold(self):
        self.set_text('''
A **B** __C__ D
**E**
''')
        self.check_eq_scope([ r'\*\*B\*\*', r'__C__', r'\*\*E\*\*' ], 'markup.bold')
        self.check_eq_scope(r'[\*_]+', 'punctuation.definition')
        self.check_default(list('AD '))

    def test_inline_markup_inside_inline_markup(self):
        self.set_text('''
A *B **C** D* E
F **G *H* I** J
''')
        self.check_eq_scope(r'\*B \*\*C\*\* D\*', 'markup.italic')
        self.check_eq_scope(r'\*H\*', 'markup.italic')
        self.check_eq_scope(r'\*\*C\*\*', 'markup.bold')
        self.check_eq_scope(r'\*\*G \*H\* I\*\*', 'markup.bold')
        self.check_eq_scope(r'\*+', 'punctuation.definition')
        self.check_default(list('AEFJ'))

    def test_bold_italic(self):
        self.set_text('''
AA *__AB__* AC
BA _**BB**_ BC
CA **_CB_** CC
DA __*DB*__ DC
EA ***EB*** EC
FA ___FB___ FC
''')
        self.check_eq_scope(r'\*__AB__\*', 'markup.italic')
        self.check_eq_scope(r'_\*\*BB\*\*_', 'markup.italic')
        self.check_eq_scope([ '_CB_', r'\*DB\*' ], 'markup.italic')
        self.check_eq_scope([ '__AB__', r'\*\*BB\*\*' ], 'markup.bold')
        self.check_eq_scope(r'\*\*_CB_\*\*', 'markup.bold')
        self.check_eq_scope(r'__\*DB\*__', 'markup.bold')
        self.check_eq_scope(r'\*+|_+', 'punctuation.definition')
        self.check_eq_scope(r'\*\*\*EB\*\*\*', 'markup.bold')
        self.check_eq_scope(r'\*\*\*EB\*\*\*', 'markup.italic')
        self.check_eq_scope(r'___FB___', 'markup.bold')
        self.check_eq_scope(r'___FB___', 'markup.italic')
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
        self.check_eq_scope([
            r'\*B\*', r'\*C\*', r'\*D\*', r'\*E\*', r'\*F\*'
            ], 'markup.italic')
        self.check_eq_scope([
            r'\*\*L\*\*', r'\*\*M\*\*', r'\*\*N\*\*',
            r'\*\*O\*\*', r'\*\*P\*\*'
            ], 'markup.bold')
        self.check_eq_scope(r'\*+', 'punctuation.definition')
        self.check_default(r'[AGKQ:;,\.?]')

    def test_inline_markup_inside_quotes_and_brackets(self):
        self.set_text('''
A "*B*" (*C*) '*D*' E
K "**L**" (**M**) '**N**' O
''')
        self.check_eq_scope([ r'\*B\*', r'\*C\*', r'\*D\*' ], 'markup.italic')
        self.check_eq_scope([ r'\*\*L\*\*', r'\*\*M\*\*', r'\*\*N\*\*' ], 'markup.bold')
        self.check_eq_scope(r'\*+', 'punctuation.definition')
        self.check_default(r'''[AEKQ"\(\)'\.]''')

    def test_inline_markup_outside_quotes_and_brackets(self):
        self.set_text('''
*"A"* *(B)* *'C'*
**"D"** **(E)** **'F'**
*"A";* *(B).* *'C':*
**"D"!** **(E)?** **'F',**
Z
''')
        self.check_eq_scope([ r'\*"A"\*', r'\*\(B\)\*', r"\*'C'\*" ], 'markup.italic')
        self.check_eq_scope([ r'\*\*"D"\*\*', r'\*\*\(E\)\*\*', r"\*\*'F'\*\*" ], 'markup.bold')
        self.check_eq_scope([ r'\*"A";\*', r'\*\(B\)\.\*', r"\*'C':\*" ], 'markup.italic')
        self.check_eq_scope([ r'\*\*"D"!\*\*', r'\*\*\(E\)\?\*\*', r"\*\*'F',\*\*" ], 'markup.bold')
        self.check_default('Z')

    def test_brackets_inside_inline_markup(self):
        self.set_text('''
*A (B C)*: D
*(K)* **(L)**
''')
        self.check_eq_scope([ r'\*A \(B C\)\*', r'\*\(K\)\*' ] , 'markup.italic')
        self.check_eq_scope( r'\*\*\(L\)\*\*', 'markup.bold')
        self.check_eq_scope(r'\*+', 'punctuation.definition')
        self.check_default(r': D')

    def test_inline_markup_combinations(self):
        self.set_text('_A _ B_C D_E _ F_ *G* **H** <a>_I_</a>')
        self.check_eq_scope([ '_A _ B_C D_E _ F_',
            r'\*G\*', '_I_' ], 'markup.italic')
        self.check_eq_scope(r'\*\*H\*\*', 'markup.bold')

    def test_escaping_of_inline_punctuation(self):
        self.set_text(r'A *\*B\** C **D\*** E')
        self.check_eq_scope(r'\*\\\*B\\\*\*', 'markup.italic')
        self.check_eq_scope(r'\*\*D\\\*\*\*', 'markup.bold')
        self.check_default(list('ACE '))

    def test_inline_markup_does_not_work_inside_words(self):
        self.set_text('A_B C_D_E')
        self.check_default('.+')

    def test_inline_markup_does_not_work_without_text(self):
        self.set_text('''
A ____ B
''')
        self.check_default('^.+$')

    def test_valid_ampersands(self):
        self.set_text('''
&
&&
A & B
A && B
& A &B && C &&D E& F&&
&G;
''')
        self.check_no_scope('^.+$', 'invalid')

    def test_valid_brackets(self):

        self.set_text('''
<
<<
A < B
A << B
A<
A<<
''')
        self.check_no_scope('^.+$', 'invalid')

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

    def test_setext_headings(self):
        self.set_text('''
A
===

B
---

C
D
======= 
E
F
-------   

Z
''')
        self.check_eq_scope('=+', 'markup.heading.1')
        self.check_eq_scope('-+', 'markup.heading.2')
        self.check_default(r'\w+')

    def test_not_setext_headings(self):
        self.set_text('''
- A
===

> B
---

C
 ======= 

D
--

E
- - -

-------
-------   

========

Z
''')
        self.check_no_scope('.+', 'markup.heading')

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
        self.check_eq_scope([ '_A_', '_C_', '_E_', '_L M_' ], 'markup.italic')
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
        self.set_text('\n\n        \n\n')
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

    def test_inline_raw_delimiters_do_not_start_fenced_block(self):
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
        self.check_eq_scope('`A`', 'markup.raw.inline.markdown')
        self.check_eq_scope('_B_', 'markup.italic')
        self.check_eq_scope(r'\*\*C\*\*', 'markup.bold')

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
''')
        self.check_eq_scope(r'- B\n', 'meta.paragraph.list')
        self.check_default(r'\nA\n')

    def test_inline_markup_inside_list_items(self):
        self.set_text('''
- `A`
- _B_
- **C**
''')
        self.check_in_scope(r'-.*$\n', 'meta.paragraph.list')
        self.check_eq_scope('`A`', 'markup.raw.inline.markdown')
        self.check_eq_scope('_B_', 'markup.italic')
        self.check_eq_scope(r'\*\*C\*\*', 'markup.bold')

    def test_multiline_list_items(self):
        self.set_text('''
 - A
 B
 - C
D

Z
''')
        self.check_eq_scope(r' - A\n B\n - C\nD\n', 'meta.paragraph.list')
        self.check_default('Z')

    def test_multiline_list_item_with_paragraph(self):
        self.set_text('''
- A

 B
C
- D

 E
F

Z
''')
        self.check_eq_scope(r'- A\n', 'meta.paragraph.list')
        self.check_eq_scope(r' B\nC\n- D\n', 'meta.paragraph.list')
        self.check_eq_scope(r' E\nF\n', 'meta.paragraph.list')
        self.check_default('Z')

    def test_4_spaces_in_multiline_list_item(self):
        self.set_text('''
- A
    B
    C

- D

    E
    F

Z
''')
        self.check_eq_scope(r'- A\n {4}B\n {4}C\n', 'meta.paragraph.list')
        self.check_eq_scope(r'- D\n', 'meta.paragraph.list')
        self.check_eq_scope(r' {4}E\n {4}F\n', 'meta.paragraph.list')
        self.check_default('Z')

    def test_4_spaces_before_nested_list_items(self):
        self.set_text('''
- A
    - B
        - C

Z
''')
        self.check_eq_scope(r'- A\n {4}- B\n {8}- C\n', 'meta.paragraph.list')
        self.check_default('Z')

    def test_fenced_block_is_not_part_of_a_list_item(self):
        self.set_text('''
- A
```
B
```

Z
''')
        self.check_eq_scope(r'- A\n', 'meta.paragraph.list')
        self.check_eq_scope(r'```\nB\b\n```\n', 'markup.raw.block.fenced')
        self.check_default('Z')

    def test_inline_links(self):
        self.set_text('''
[A](B)
[C]  (D)
[E](F "G")
![A](B)
![C]  (D)
![E](F "G")
Z
''')
        self.check_eq_scope([
            r'^\[A\]\(B\)',
            r'^\[C\]\s+\(D\)',
            r'^\[E\]\(F "G"\)'
            ], 'meta.link.inline')
        self.check_eq_scope([
            r'^!\[A\]\(B\)',
            r'^!\[C\]\s+\(D\)',
            r'^!\[E\]\(F "G"\)'
            ], 'meta.image.inline')
        self.check_eq_scope(list('ACE'), 'string.other.link.title')
        self.check_eq_scope(list('BDF'), 'markup.underline.link')
        self.check_eq_scope('G', 'string.other.link.description.title')
        self.check_eq_scope([ r'!', r'\[', r'\]' ], 'punctuation.definition')
        self.check_default('Z')

    def test_reference_links(self):
        self.set_text('''
[A][B]
[C]  [D]
![E][F]
![G]  [H]
Z
''')
        self.check_eq_scope(r'\[A\]\[B\]', 'meta.link.reference')
        self.check_eq_scope(r'\[C\]\s+\[D\]', 'meta.link.reference')
        self.check_eq_scope(r'!\[E\]\[F\]', 'meta.image.reference')
        self.check_eq_scope(r'!\[G\]\s+\[H\]', 'meta.image.reference')
        self.check_eq_scope(list('ACEG'), 'string.other.link.title')
        self.check_eq_scope(list('BDFH'), 'constant.other.reference.link')
        self.check_eq_scope([ r'!', r'\[', r'\]' ], 'punctuation.definition')
        self.check_default('Z')

    def test_implicit_links(self):
        self.set_text('''
[A][]
  [B]  []  
![C][]
  ![D]  []  
Z
''')
        self.check_eq_scope([ r'\[A\]\[\]', r'\[B\]  \[\]' ],
            'meta.link.reference')
        self.check_eq_scope([ r'!\[C\]\[\]', r'!\[D\]  \[\]' ],
            'meta.image.reference')
        self.check_eq_scope(list('ABCD'), 'constant.other.reference.link')
        self.check_eq_scope(r'[!\[\]]', 'punctuation.definition')
        self.check_default('Z')

    def test_multiline_links_not_supported(self):
        self.set_text('''
[A
B](C)
[D
E][F]
![A
B](C)
![D
E][F]
''')
        self.check_default('.+')

    def test_inline_markup_inside_links(self):
        self.set_text('''
[__A__](B)
[_C_][D]
![__E__](F)
![_G_][H]
Z
''')
        self.check_eq_scope(r'\[__A__\]\(B\)', 'meta.link.inline')
        self.check_eq_scope(r'\[_C_\]\[D\]', 'meta.link.reference')
        self.check_eq_scope(r'!\[__E__\]\(F\)', 'meta.image.inline')
        self.check_eq_scope(r'!\[_G_\]\[H\]', 'meta.image.reference')
        self.check_eq_scope([ '__A__', '__E__' ], 'markup.bold')
        self.check_eq_scope([ '_C_', '_G_' ], 'markup.italic')
        self.check_default('Z')

    def test_inline_markup_outside_links(self):
        self.set_text('''
**[A](X)**
__[B][X]__
*![C](X)*
_![D][X]_
Z
''')
        self.check_eq_scope(r'\*\*\[A\]\(X\)\*\*', 'markup.bold')
        self.check_eq_scope(r'__\[B\]\[X\]__', 'markup.bold')
        self.check_eq_scope(r'\*!\[C\]\(X\)\*', 'markup.italic')
        self.check_eq_scope(r'_!\[D\]\[X\]_', 'markup.italic')
        self.check_default('Z')

    def test_references(self):
        self.set_text('''
[A]: B "C"
[D]:<E> 'F'
  [K]: L (M)  
[N]: O
Z
''')
        self.check_eq_scope(r'\[.*?(?=\s*$)', 'meta.link.reference.def')
        self.check_eq_scope(r'''[\[\]:'"()]''', 'punctuation')
        self.check_eq_scope(list('ADKN'), 'constant.other.reference.link')
        self.check_eq_scope(list('BELO'), 'markup.underline.link')
        self.check_eq_scope(list('CFM'), 'string.other.link.description.title')
        self.check_default('Z')

    def test_supported_urls(self):
        self.set_text('''
http://A.IT Z
https://C.COM Z
ftp://E.GOOGLE Z
http://H.I.XX Z
http://K.XX/ Z
http://M.XX/O?P=Q&R=S Z
http://Q.XX:123 Z
http://Q.W.XX:123/ Z
http://ПРИВЕТ.МИР Z
Z
''')
        self.check_eq_scope(r'\S+://\S+', 'markup.underline.link')
        self.check_eq_scope(r'\S+://\S+', 'meta.link.inet')
        self.check_default('Z')

    def test_urls_with_italic_markup(self):
        self.set_text('''
_A http://K.com_ Z
*C http://L.com* Z
_E http://M.com?a=b_ Z
Z
''')
        self.check_eq_scope(r'http://K\.com', 'markup.underline.link')
        self.check_eq_scope(r'_A http://K\.com_', 'markup.italic')
        self.check_eq_scope(r'_', 'punctuation.definition')
        
        self.check_eq_scope(r'http://L\.com', 'markup.underline.link')
        self.check_eq_scope(r'\*C http://L\.com\*', 'markup.italic')
        self.check_eq_scope(r'\*', 'punctuation.definition')

        self.check_eq_scope(r'http://M\.com\?a=b', 'markup.underline.link')
        self.check_eq_scope(r'_E http://M\.com\?a=b_', 'markup.italic')
        self.check_eq_scope(r'_', 'punctuation.definition')

        self.check_default('Z')

    def test_urls_with_bold_markup(self):
        self.set_text('''
__E http://M.com__ Z
Z
''')
        self.check_eq_scope(r'http://M\.com', 'markup.underline.link')
        self.check_eq_scope(r'__E http://M\.com__', 'markup.bold')
        self.check_eq_scope(r'__', 'punctuation.definition')
        
        self.check_default('Z')

    def test_unsupported_urls(self):
        self.set_text('''
http://A
http://A.B
http://A:80
http://A:80.C
ssh://B.C
http://D/E
http://A?B.C
''')
        self.check_default('.+')

    def test_urls_in_brackes(self):
        self.set_text('''
<http://A.IT> Z
<https://C.COM> Z
<ftp://E.GOOGLE> Z
<http://H.I.XX> Z
<http://K.XX/> Z
<http://M.XX/O?P=Q&R=S> Z
<http://Q.XX:123> Z
<http://Q.W.XX:123/> Z
Z
''')
        self.check_eq_scope(r'http://A\.IT', 'markup.underline.link')
        self.check_eq_scope(r'^\S+://\S+', 'meta.link.inet')
        self.check_eq_scope(r'[<>]', 'punctuation.definition')
        self.check_default('Z')

    def test_emails(self):
        self.set_text('''
<A@B.XX>
<mailto:D@E.XX>
O@P.XX
mailto:R@S.XX
Z
''')
        self.check_eq_scope(r'A@B.XX', 'markup.underline.link')
        self.check_eq_scope(r'mailto:R@S.XX', 'markup.underline.link')
        self.check_eq_scope(r'[^\s@]+@\S+', 'meta.link.email')
        self.check_eq_scope(r'[<>]', 'punctuation.definition')
        self.check_default('Z')

    def test_strikethrough(self):
        self.set_text('''
A ~~B~~ ~~C D~~ E
''')
        self.check_eq_scope([ '~~B~~', '~~C D~~' ], 'markup.strikethrough')
        self.check_eq_scope('~~', 'punctuation.definition.strikethrough')
        self.check_default(list('AE'))

    def test_unsupported_strikethrough(self):
        self.set_text('''
~~A
B~~
~~ C~~
~~D ~~
E~~F~~
''')
        self.check_default('.+')

    def test_strikethrough_with_bold_italic(self):
        self.set_text('''
*__~~A~~__*
*~~__B__~~*
~~*__C__*~~
___~~D~~___
~~___E___~~
Z
''')
        self.check_eq_scope([
            r'~~A~~', r'~~__B__~~', r'~~\*__C__\*~~',
            r'~~D~~', r'~~___E___~~'
            ], 'markup.strikethrough')
        self.check_eq_scope([
            r'__~~A~~__', r'__B__', r'__C__',
            r'___~~D~~___', r'___E___'
            ], 'markup.bold')
        self.check_eq_scope([
            r'\*__~~A~~__\*', r'\*~~__B__~~\*', r'\*__C__\*',
            r'___~~D~~___', r'___E___'
            ], 'markup.italic')
        self.check_eq_scope(r'~+|_+|\*+', 'punctuation.definition')
        self.check_default('Z')

    def test_html_tags(self):
        self.set_text('''
A<br>
<li>B
<a href="http://C.D">E</a>
''')
        self.check_default([ r'\nA', r'\n', r'B\n', 'E' ])
        self.check_eq_scope([ '<br>', '<li>',
            '<a href="http://C.D">', '</a>' ],
            'meta.tag')

    def test_block_tags_turn_off_markdown_markup(self):
        self.set_text('''
<p>
*A* ~~B~~ __C__
</p> 
<div>*D* ~~E~~ __F__</div> 
''')
        self.check_no_scope(list('ABCDEF'), 'markup')

    def test_inline_markup_combined_with_html(self):
        self.set_text('<a>_A_</a>')
        self.check_eq_scope('_A_', 'markup.italic')
        self.check_eq_scope([ '<a>', '</a>' ], 'meta.tag')

    def test_horisontal_lines(self):
        self.set_text('''
***

* * *

___

 __ __ __

  - - - 

   ----------------      

---_---

Z
''')
        self.check_eq_scope([
            r'\*\*\*\n',
            r'\* \* \*\n',
            r'___\n',
            r' __ __ __\n',
            r'  - - - \n',
            r'   -----+ +\n'
            ], 'meta.separator')
        self.check_default(['---_---', 'Z'])

    def test_horisontal_lines_break_paragraphs(self):
        self.set_text('''
A
- - -
Z
''')
        self.check_eq_scope('- - -\n', 'meta.separator')
        self.check_default(['A', 'Z'])
