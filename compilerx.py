
# 99105453 Mohammad Rezaei
# 99105718 Arsalan Masoudifard
from collections import defaultdict
from anytree import Node
from anytree import RenderTree
import json

def get_next_token():
    global cursor
    global line_num
    if isEOF():
        return line_num, "$", '$'
    char = input_code_as_str[cursor]
    token_type = get_token_type(char)

    if token_type == "WHITESPACE":
        if char == '\n':
            line_num += 1
        cursor += 1
        return get_next_token()

    elif token_type == "SYMBOL":
        if char == '=':
            if cursor < len(input_code_as_str) - 1 and input_code_as_str[cursor + 1] == '=':
                cursor += 2
                return line_num, "SYMBOL", '=='
            elif cursor < len(input_code_as_str) - 1 and get_token_type(input_code_as_str[cursor + 1]) == 'INVALID':
                lexical_errors[line_num].append((char+input_code_as_str[cursor + 1], 'Invalid input'))
                cursor += 2
                return False
                
        elif char == '*':
            if cursor < len(input_code_as_str) - 1 and input_code_as_str[cursor + 1] == '/':
                cursor += 2
                lexical_errors[line_num].append(('*/', 'Unmatched comment'))
                return False
            if cursor < len(input_code_as_str) - 1 and get_token_type(input_code_as_str[cursor + 1]) == 'INVALID':
                lexical_errors[line_num].append((char+input_code_as_str[cursor + 1], 'Invalid input'))
                cursor += 2
                
                return False
        cursor += 1
        return line_num, "SYMBOL", char

    elif token_type == "NUM":
        number, err = get_whole_number(char)
        if not err:
            return line_num, "NUM", number
        lexical_errors[line_num].append((number, 'Invalid number'))

    elif token_type == "IDORKEYWORD":
        name, err = get_whole_idkeyword(char)
        if not err:
            return line_num, get_from_table(name), name
        lexical_errors[line_num].append((name, 'Invalid input'))

    elif token_type == "COMMENT":
        find_comment()

    elif token_type == "INVALID":
        lexical_errors[line_num].append((char, 'Invalid input'))
        cursor += 1

def isEOF():
    return cursor >= len(input_code_as_str)


    
def get_token_type(char):
    if char in [' ', '\t', '\n', '\r', '\v', '\f']:  
        return "WHITESPACE"
    elif char in [';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '=', '<']:  
        return "SYMBOL"
    elif char.isdigit():  
        return "NUM"
    elif char.isalnum():  
        return "IDORKEYWORD"
    elif char == '/':  
        return "COMMENT"
    else:  
        return "INVALID"
    
def get_whole_number(num):
    global cursor
    while cursor + 1 < len(input_code_as_str):
        cursor += 1
        temp_char = input_code_as_str[cursor]
        temp_type = get_token_type(temp_char)
        if temp_type == "NUM":
            num += temp_char
        elif temp_type == "WHITESPACE" or temp_type == "SYMBOL":
            return num, False
        else:
            num += temp_char
            cursor += 1
            return num, True
    cursor += 1
    return num, False

def get_whole_idkeyword(name):
    global cursor
    while cursor + 1 < len(input_code_as_str):
        cursor += 1
        temp_char = input_code_as_str[cursor]
        temp_type = get_token_type(temp_char)
        if temp_type == "NUM" or temp_type == "IDORKEYWORD":
            name += temp_char
        elif temp_type == "WHITESPACE" or temp_type == "SYMBOL":
            return name, False
        else:
            name += temp_char
            cursor += 1
            return name, True
    cursor += 1
    return name, False

def get_from_table(name):
    if name in symbol_table['KEYWORD']:
        return "KEYWORD"
    else:
        if name not in symbol_table['ID']:
            symbol_table['ID'].append(name)   
        return "ID"
    
def find_comment():
        global cursor
        global line_num
        beginning_line_number = line_num
        lexeme = input_code_as_str[cursor]
        if cursor + 1 == len(input_code_as_str):
            lexical_errors[line_num].append((lexeme, 'Invalid input')) 
            cursor += 1
            return None, True

        next_char = input_code_as_str[cursor + 1]
        if next_char != "*":
            lexical_errors[line_num].append(
                (lexeme + (next_char if get_token_type(next_char) == "INVALID" else ''), 'Invalid input'))
            
            cursor += 1
            if get_token_type(next_char) == "INVALID": 
                cursor += 1
            return None, True

        

        while cursor + 1 < len(input_code_as_str):
            cursor += 1
            temp_char = input_code_as_str[cursor]
            
            if cursor + 1 < len(input_code_as_str):
                if temp_char == '*' and input_code_as_str[cursor + 1] == '/':
                    cursor += 2
                    return lexeme + '*/', False
            else:
                lexeme += input_code_as_str[-1]
                cursor += 1
                lexical_errors[beginning_line_number].append((get_short_comment(lexeme), 'Unclosed comment'))
                return None, True

            if temp_char == '\n':
                line_num += 1
            lexeme += temp_char

        cursor += 1
        return lexeme, False

def get_short_comment(comment):
    return comment[:7] + '...' if len(comment) >= 7 else comment


first = dict()  # {T: [First(T)]}
follow = dict()  # {T: [Follow(T)]}
predict = dict()  # {No: [First(Prod(No))]}
productions = dict()  # {T: [prod numbers]}
grammar = dict()  # {No: Prod}
pg = dict()  # {No: Prod}

def init_grammar():
    with open('./self/first.txt', 'r') as f:
        for line in f.readlines():
            line_parts = line.strip().replace('\t', ' ').split(' ')
            first[line_parts[0]] = line_parts[1:]
    with open('./self/follow.txt', 'r') as f:
        for line in f.readlines():
            line_parts = line.strip().replace('\t', ' ').split(' ')
            follow[line_parts[0]] = line_parts[1:]
 
    with open('./self/predict.txt', 'r') as f:
        for line in f.readlines():
            line_parts = line.strip().replace('\t', ' ').split(' ')
            predict[int(line_parts[0])] = line_parts[1:]
    with open('./grammar.txt', 'r') as f:
        for idx, line in enumerate(f.readlines()):
            rhs = line.strip().split('->')[1]  # right-hand side
            grammar[idx + 1] = rhs.strip().split(' ')
    with open('./grammar.txt', 'r') as f:
        temp_list = []
        for idx, line in enumerate(f.readlines()):
            lhs = line.strip().split('->')[0]  # left-hand side
            if lhs.strip() not in productions:
                temp_list.clear()
            temp_list.append(idx+1)
            productions[lhs.strip()] = temp_list.copy()
            



def is_non_terminal(word):
    return word in productions.keys()


def is_action_symbol(word: str):
    return word.startswith('#')


class Parser:
    def __init__(self):
        init_grammar()
        self.root = Node('Program')
        self.lookahead = None
        self.syntax_errors = []
        self.unexpected_eof_reached = False



    def run(self):
        self.lookahead = get_next_token()
        while not self.lookahead:
            self.lookahead = get_next_token()
        self.call_procedure(self.root)

    def call_procedure(self, non_terminal: Node):
        print(self.lookahead, " ", non_terminal.name)
        for rule_number in productions[non_terminal.name]:
            if self.lookahead[2] in predict[rule_number] or self.lookahead[1] in predict[rule_number]:  # selecting the appropriate production
                self.call_rule(non_terminal, rule_number)
                break
        else:  # is visited when no corresponding production was found
            if self.lookahead[2] in follow[non_terminal.name]:
                if "EPSILON" not in first[non_terminal.name]:  # missing T
                    self.syntax_errors.append(f'#{self.lookahead[0]} : syntax error, missing {non_terminal.name}')
                non_terminal.parent = None  # Detach Node
                return  # exit
            else:  # illegal token
                if self.eof_reached():
                    self.syntax_errors.append(f'#{self.lookahead[0]} : syntax error, Unexpected EOF')
                    self.unexpected_eof_reached = True
                    non_terminal.parent = None  # Detach Node
                    return
                # in samples, illegals are treated differently:
                illegal_lookahead = self.lookahead[2]
                if self.lookahead[1] in ['NUM', 'ID']:
                    illegal_lookahead = self.lookahead[1]
                #
                self.syntax_errors.append(f'#{self.lookahead[0]} : syntax error, illegal {illegal_lookahead}')
                self.lookahead = get_next_token()
                while not self.lookahead:
                    self.lookahead = get_next_token()
                
                self.call_procedure(non_terminal)

    def call_rule(self, parent, rule_number):
        for part in grammar[rule_number]:
            if self.unexpected_eof_reached:
                return
            if is_action_symbol(part):
                self.code_generator.call_routine(part, self.lookahead)
            elif is_non_terminal(part):
                node = Node(part, parent=parent)
                self.call_procedure(node)
            else:
                self.call_match(part, parent)

    def call_match(self, expected_token, parent):
        correct = False
        if expected_token in ['NUM', 'ID']:
            correct = self.lookahead[1] == expected_token
        elif (expected_token in symbol_table['KEYWORD']) or (get_token_type(expected_token) == "SYMBOL" or expected_token == '=='):
            correct = self.lookahead[2] == expected_token

        if correct:
            Node(f'({self.lookahead[1]}, {self.lookahead[2]})', parent=parent)
            self.lookahead = get_next_token()
            while not self.lookahead:
                self.lookahead = get_next_token()
        elif expected_token == "EPSILON":
            Node('epsilon', parent=parent)
        elif expected_token == "$":
            Node('$', parent=parent)
        else:
            self.syntax_errors.append(f'#{self.lookahead[0]} : syntax error, missing {expected_token}')

    def eof_reached(self):
        return self.lookahead[1] == "$"

def save_parse_tree(parser: Parser):
    with open('parse_tree.txt', 'w', encoding='utf-8') as f:
        for pre, fill, node in RenderTree(parser.root):
            f.write("%s%s\n" % (pre, node.name))
    
if __name__ == '__main__':
    symbol_table = {'KEYWORD': ['if', 'else', 'void', 'int', 'repeat', 'break', 'until', 'return'],
            'ID': []}
    input_code_as_str = None
    with open("tests/T08/input.txt", 'r') as f:
        input_code_as_str = ''.join([line for line in f.readlines()])
    cursor = 0
    line_num = 1
    lexical_errors = defaultdict(list) 
    p = Parser()


    p.run()
    save_parse_tree(p)
    print("\n".join(p.syntax_errors))
    exit(0)
    

    tokens = []
    lineToken = ""
    currentLine = 0


    while True:
        token = get_next_token()
        if token is not None and type(token) is not bool:
            if (currentLine != token[0] and token[0] > currentLine and currentLine != 0) or token[1] == "$":
                tokens.append(str(currentLine)+".\t" + lineToken + "\n")
                lineToken = ""
            currentLine = token[0]
            lineToken += "("+token[1]+", "+token[2]+") "

        if token == None or token == False:
            continue
        elif token[1] == "$":
            break
        else:
            pass

    with open('tokens.txt', 'w') as file:
         file.writelines( tokens )
 
    
    symbols = []
    counter = 0
    for i in symbol_table:
        for j in symbol_table[i]:
            counter += 1
            symbols.append(str(counter)+".\t"+ j+"\n")
    with open('symbol_table.txt', 'w') as file:
         file.writelines( symbols )
         
    errors = []
    for i in lexical_errors:
        e = ""
        for j in lexical_errors[i]:
            e += "("+j[0]+", " +j[1]+") "
        errors.append(str(i)+".\t"+e+"\n")
    if len(errors) == 0:
        errors.append("There is no lexical error.")
    with open('lexical_errors.txt', 'w') as file:
         file.writelines( errors )




    
 
    