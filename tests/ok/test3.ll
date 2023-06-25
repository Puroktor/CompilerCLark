AST дерево
...
├ function
│ ├ returns 
│ │ └ boolean
│ ├ cond
│ ├ params_list
│ └ ...
│   └ return
│     └ >=
│       ├ 2 (int)
│       └ 3 (int)
├ function
│ ├ returns 
│ │ └ double
│ ├ calc
│ ├ params_list
│ └ ...
│   ├ var
│   │ ├ boolean
│   │ └ =
│   │   ├ f
│   │   └ False (bool)
│   ├ while
│   │ ├ f
│   │ └ ...
│   └ if
│     ├ f
│     ├ return
│     │ └ 1 (int)
│     └ ...
│       ├ if
│       │ ├ &&
│       │ │ ├ >
│       │ │ │ ├ 1 (int)
│       │ │ │ └ 2 (int)
│       │ │ └ call
│       │ │   └ cond
│       │ └ ...
│       │   └ return
│       │     └ 0 (int)
│       └ return
│         └ 3.5 (float)
└ function
  ├ returns 
  │ └ void
  ├ main
  ├ params_list
  └ ...
    ├ array-decl
    │ ├ string
    │ ├ arr
    │ └ 999 (int)
    ├ var
    │ ├ int
    │ └ =
    │   ├ n
    │   └ call
    │     ├ parseInt
    │     └ call
    │       └ readLine
    ├ for
    │ ├ var
    │ │ ├ int
    │ │ └ =
    │ │   ├ i
    │ │   └ 0 (int)
    │ ├ <
    │ │ ├ i
    │ │ └ n
    │ ├ ...
    │ │ └ =
    │ │   ├ i
    │ │   └ +
    │ │     ├ i
    │ │     └ 1 (int)
    │ └ ...
    │   └ =
    │     ├ element[]
    │     │ ├ arr
    │     │ └ i
    │     └ call
    │       └ readLine
    ├ call
    │ ├ print
    │ └ element[]
    │   ├ arr
    │   └ 0 (int)
    └ call
      └ calc
После семантической проверки
...
├ function
│ ├ returns 
│ │ └ boolean
│ ├ cond : boolean (), global, 0
│ ├ params_list
│ └ ...
│   └ return : void
│     └ >= : boolean
│       ├ 2 (int) : int
│       └ 3 (int) : int
├ function
│ ├ returns 
│ │ └ double
│ ├ calc : double (), global, 0
│ ├ params_list
│ └ ...
│   ├ var
│   │ ├ boolean
│   │ └ =
│   │   ├ f : boolean, local, 0
│   │   └ False (bool) : boolean
│   ├ while
│   │ ├ f : boolean, local, 0
│   │ └ ...
│   └ if
│     ├ f : boolean, local, 0
│     ├ return : void
│     │ └ convert : double
│     └ ...
│       ├ if
│       │ ├ && : boolean
│       │ │ ├ > : boolean
│       │ │ │ ├ 1 (int) : int
│       │ │ │ └ 2 (int) : int
│       │ │ └ call
│       │ │   └ cond : boolean (), global, 0
│       │ └ ...
│       │   └ return : void
│       │     └ convert : double
│       └ return : void
│         └ 3.5 (float) : double
└ function
  ├ returns 
  │ └ void
  ├ main : void (), global, 0
  ├ params_list
  └ ...
    ├ array-decl
    │ ├ string
    │ ├ arr
    │ └ 999 (int) : int
    ├ var
    │ ├ int
    │ └ =
    │   ├ n : int, local, 1
    │   └ call
    │     ├ parseInt : int (string), global, built-in
    │     └ call
    │       └ readLine : string (), global, built-in
    ├ for : void
    │ ├ var
    │ │ ├ int
    │ │ └ =
    │ │   ├ i : int, local, 2
    │ │   └ 0 (int) : int
    │ ├ < : boolean
    │ │ ├ i : int, local, 2
    │ │ └ n : int, local, 1
    │ ├ ...
    │ │ └ =
    │ │   ├ i : int, local, 2
    │ │   └ + : int
    │ │     ├ i : int, local, 2
    │ │     └ 1 (int) : int
    │ └ ...
    │   └ =
    │     ├ element[] : string
    │     │ ├ arr : string[][999 (int)], local, 0
    │     │ └ i : int, local, 2
    │     └ call
    │       └ readLine : string (), global, built-in
    ├ call
    │ ├ print : void (string), global, built-in
    │ └ element[] : string
    │   ├ arr : string[][999 (int)], local, 0
    │   └ 0 (int) : int
    └ call
      └ calc : double (), global, 0
