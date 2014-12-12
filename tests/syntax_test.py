import sublime
import unittest

SINGLE_SCOPE = 1

def make_human_readable(string):
    return (string
        .replace('\n', r'\n')
        .replace('\r', r'\r')
        .replace('\t', r'\t')
        )

class SyntaxTestCase(unittest.TestCase):
    def setUp(self):
        self.view = sublime.active_window().new_file()
        self.view.settings().set('auto_indent', False)

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.view.window().focus_view(self.view)
            self.view.window().run_command("close_file")

    def set_syntax_file(self, syntax_file):
        assert(self.view)
        self.view.set_syntax_file(syntax_file)

    def set_text(self, string):
        self.view.run_command("select_all")
        self.view.run_command("left_delete")
        self.view.run_command("insert", {"characters": string})

    def set_default_scope(self, default_scope):
        self.default_scope = default_scope

# TODO:
# 1. If region.begin() has scopes A and B, but the rest
# of the text has only scope B then extract_scope(begin)
# will select only region.begin
# 2. Add methods of checking that given region
# - has scope
# - has one scope
# - has one scope and scope has exactly the same region
# - has scope and scope has exactly the same region
# 3. Use extract_scope to find positions to check.

    def has_scope(self, region, scope):
        pos = region.begin()
        scope_region = self.view.extract_scope(pos)
        if not scope_region.contains(region):
            return False
        return self.view.score_selector(pos, scope) > 0

    def has_single_scope(self, region, scope):
        if not self.has_scope(region, scope):
            return False
        begin_scope = self.view.scope_name(region.begin())
        scopes = map(lambda pos: self.view.scope_name(pos),
            range(region.begin() + 1, region.end()))
        return (len(begin_scope.split()) == 1 and
            all(map(lambda scope: scope == begin_scope, scopes)))

    def verify_pattern(self, pattern, scope, flags):
        regions = self.view.find_all(pattern)
        self.assertTrue(regions, 'Cannot find pattern /{}/'.format(pattern))
        check = self.has_single_scope if flags == SINGLE_SCOPE else self.has_scope
        for region in regions:
            self.assertTrue(check(region, scope),
                'Text "{}" found by /{}/ does not match scope "{}"'.format(
                    make_human_readable(self.view.substr(region)),
                    pattern,
                    scope
                    )
                )

    def verify_scope(self, patterns, scope, flags = 0):
        if type(patterns) is not list:
            patterns = [ patterns ]
        for pattern in patterns:
            self.verify_pattern(pattern, scope, flags)

    def verify_default(self, patterns):
        self.verify_scope(patterns, self.default_scope, SINGLE_SCOPE)
