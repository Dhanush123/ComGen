class JavaDocListener(Java9Listener):

    # methodDeclaration
    #   :   methodModifier* methodHeader methodBody
    #   ;
    def enterMethodDeclaration(self, ctx: Java9Parser.MethodDeclarationContext):
        previous_token_index = ctx.getSourceInterval()[0] - 1
        previous_token = ctx.parser.getTokenStream(
        ).tokens[previous_token_index]
        method_name = ctx.methodHeader().methodDeclarator().identifier().getText()
        javadoc = previous_token.text if previous_token.type == Java9Lexer.JAVADOC_COMMENT else None
        print('method: {}, javadoc: {}'.format(method_name, javadoc))


if __name__ == '__main__':

    code = """
        public class X {

          public static String mu() { return null; }

          /**
           * Some random comment
           */
          public int testM() {
            return 42;
          }
        }
    """
    input_stream = antlr4.InputStream(code)
    parser = Java9Parser(antlr4.CommonTokenStream(Java9Lexer(input_stream)))

    tree = parser.ordinaryCompilation()

    doc_listener = JavaDocListener()
    walker = antlr4.ParseTreeWalker()
    walker.walk(doc_listener, tree)
