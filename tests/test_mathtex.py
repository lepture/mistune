from mistune import Markdown, AstRenderer, HTMLRenderer, plugins
from tests import BaseTestCase, fixtures

def load_plugin(plugin_name, ast=False):
    _plugin = getattr(plugins, "plugin_{}".format(plugin_name))

    class TestPlugin(BaseTestCase):
        md = Markdown(renderer=HTMLRenderer(escape=False), plugins=[_plugin])


    def test_ast_renderer(self):
        """ Test the AST JSON renderer. This shows up as one test in the output, so print statements are listed for each phrase processed to help in test verification (output is supressed in most testing contexts, of course). """
        self.maxDiff = None
        md = Markdown(renderer=AstRenderer(), plugins=[_plugin])
        data = fixtures.load_json(plugin_name + ".json")
        print("\n")

        def find_type(ref, badtype):
            if type(ref) is list:
                for subref in ref:
                    if find_type(subref, badtype):
                        return(True)
            elif type(ref) is dict:
                if badtype == ref['type']:
                    return(True)
                return(find_type(ref.values(), badtype))
            return(False)

        def run_json_phrase(phrase):
            if 'message' in phrase:
                message = phrase['message'] 
            else:
                message = phrase['text']

            if 'no_type' in phrase and phrase['no_type']:
                message += f"  (expect no '{phrase['no_type']}' token)"


            print("Run " + message)

            # - add more useful debugging information in case the assertion fails
            try:
                message += "\n\n**Markdown Rendered**: " + str(md(phrase["text"])).replace("'", '"')
            except Exception as e:
                message += f"\n\nAttempting to render markdown fails with {e}"
            if "tokens" in phrase:
                message += ("\n\n**Expected**: " + str( phrase["tokens"]).replace("'", '"'))
            
            #try:
            if 'no_type' in phrase and phrase['no_type']:
                self.assertFalse(find_type(md(phrase["text"]), phrase['no_type']), message)
            else:
                self.assertEqual(md(phrase["text"]), phrase["tokens"], message)
            #except AssertionError as ae:
            #    print("\n\n" + message)

        if type(data) is list:
        
            for phrase in data:
                run_json_phrase(phrase)
        else:
            run_json_phrase(data)

    if ast:
        test_ast_renderer.__doc__ = "Run {} ast renderer".format(plugin_name)
        setattr(TestPlugin, "test_ast_renderer", test_ast_renderer)

    TestPlugin.load_fixtures(plugin_name + ".txt")
    globals()["TestPlugin_" + plugin_name] = TestPlugin

load_plugin('mathblock', True)
load_plugin('mathspan', True)