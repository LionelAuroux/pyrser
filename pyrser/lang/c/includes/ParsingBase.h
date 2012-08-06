/*
** Copyright (C) 2012 Candiotti Adrien 
**
** This program is free software: you can redistribute it and/or modify
** it under the terms of the GNU General Public License as published by
** the Free Software Foundation, either version 3 of the License, or
** (at your option) any later version.
**
** This program is distributed in the hope that it will be useful,
** but WITHOUT ANY WARRANTY; without even the implied warranty of
** MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
**
** See the GNU General Public License for more details.
**
** You should have received a copy of the GNU General Public License
** along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef __PARSING_BASE__
#define __PARSING_BASE__

/* Multipliers */
#define Multiplier(fct, ...) 	((const s_cb*)__oneArg(fct, ARRAY(__VA_ARGS__)))

#define ZeroOrN(...) 		Multiplier(__zeroOrN, __VA_ARGS__)
#define OneOrN(...) 		Multiplier(__oneOrN, __VA_ARGS__)
#define ZeroOrOne(...) 		Multiplier(__zeroOrOne, __VA_ARGS__)
#define Until(...) 		Multiplier(__until, __VA_ARGS__)
#define Expression(...) 	Multiplier(allTrue, __VA_ARGS__)

#define multiplier(fct, ...) 	fct(ARRAY(__VA_ARGS__))

#define zeroOrN(...) 		multiplier(__zeroOrN, __VA_ARGS__)
#define oneOrN(...) 		multiplier(__oneOrN, __VA_ARGS__)
#define zeroOrOne(...) 		multiplier(__zeroOrOne, __VA_ARGS__)
#define until(...) 		multiplier(__until, __VA_ARGS__)
#define expression(...) 	multiplier(allTrue, __VA_ARGS__)

/* Alt */
#define Alt(...) 		Multiplier(__alt, __VA_ARGS__)
#define alt(...) 		multiplier(__alt, __VA_ARGS__)

/* NonTerminal */
#define rule(class, rule, ctx)	__##class##__##rule##Rule(ctx)
#define Rule(class, rule, ctx)	(s_cb*)__oneArg(__##class##__##rule##Rule, ctx)

/* Hooks */
#define hook(class, hook, ctx)	__##class##__##hook##Hook(ctx)
#define Hook(class, hook, ctx)	(s_cb*)__oneArg(__##class##__##hook##Hook, ctx)

/* Negation */
#define negation(...)		multiplier(__not, __VA_ARGS__)
#define Negation(...) 		Multiplier(__not, __VA_ARGS__)

#define complement(...) 	multiplier(__complement, __VA_ARGS__)
#define Complement(...) 	Multiplier(__complement, __VA_ARGS__)

bool		allTrue(const s_cb* aPredicats[]);
bool		__zeroOrN(const s_cb* predicats[]);
bool		__oneOrN(const s_cb* predicats[]);
bool		__zeroOrOne(const s_cb* predicats[]);
bool		__not(const s_cb* predicats[]);
bool		__complement(const s_cb* predicats[]);
bool		__alt(const s_cb* predicats[]);
bool		__until(const s_cb* prediact[]);

#endif /* __PARSING_BASE__ */
