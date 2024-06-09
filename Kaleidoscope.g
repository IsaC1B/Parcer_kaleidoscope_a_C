start: program;

program  : functiondef* expression;

functiondef:  DEF nombre LPAR (parameter (',' parameter)*)?  RPAR LCBR expression RCBR;

parameter: nombre | list | functioncall;

@expression:
	  parexpression
	| conditional
	| functioncall
	| arithmetic_exp
	| number 
	| variable
    | list ;

parexpression:
  LPAR expression RPAR;

conditional:
	IF LPAR logicalexpression RPAR LCBR expression RCBR ELSE LCBR expression RCBR;

functioncall:
	nombre LPAR (expression (',' expression)*)* RPAR;

arithmetic_exp:
	expression operator expression;

variable: nombre;

list: nombre LPAR (expression (',' expression)*)* RPAR;

operator:
	ADD
	| SUB
	| MUL
	| DIV
	| MOD;

logicalexpression:
	expression operatorbool expression
	| TRUE
	| FALSE	;

operatorbool:
	LT
	| GT
	| LEQ
	| GEQ
	| EQ
	| NEQ ;

// Se ignoran comentarios
OPEN_COMMENT :  '/\*';
CLOSE_COMMENT :  '\*/';
COMMENT : OPEN_COMMENT '.*?' CLOSE_COMMENT (%ignore);

// Operaciones aritméticas
ADD  :  '\+';
SUB  :  '-';
MUL  :  '\*';
DIV  :  '/';
MOD  :  '%';

// Operaciones booleanas
LT  :  '<';
GT  :  '>';
LEQ :  '<=';
GEQ :  '>=';
EQ  :  '==';
NEQ  : '!=';

// Definición de Paréntesis
LPAR : '\(';
RPAR : '\)';
LCBR : '{';
RCBR : '}';

nombre: NOMBRE;

// Números
number: '[0-9]+';

// Nombres de funciones palabras reservadas
NOMBRE: '[a-zA-Z]+'
	(%unless
		DEF: 'def';
		IF    : 'if';
		ELSE  : 'else';
		TRUE  : 'true';
		FALSE : 'false';		
	);

// Se ignoran espacios en blanco, tabulaciones y nuevas líneas.
WS: '[ \t\r\n]+' (%ignore);