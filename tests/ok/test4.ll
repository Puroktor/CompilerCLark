declare i32 @read_int()
declare double @read_double()
declare i8 @read_char()
declare void @print_int(i32)
declare void @print_double(double)
declare void @print_char(i8)
declare void @print_str(i8*)
declare void @llvm.memcpy.p0i32.p0i32.i32(i32*, i32*, i32, i1)
declare void @llvm.memcpy.p0i1.p0i1.i32(i1*, i1*, i32, i1)
declare void @llvm.memcpy.p0i8.p0i8.i32(i8*, i8*, i32, i1)
declare void @llvm.memcpy.p0double.p0double.i32(double*, double*, i32, i1)


define i32 @_main () {
%n = alloca i32
%call.read_int.0 = call i32 @read_int()
store i32 %call.read_int.0, i32* %n
%n.0 = load i32, i32* %n
%arr.0 = alloca i32, i32 %n.0
%arr = alloca i32*
store i32* %arr.0, i32** %arr

br label %for.head.0
for.head.0:
%k = alloca i32
%k.0 = add i32 0, 0
store i32 %k.0, i32* %k
br label %for.cond.0

for.cond.0:
%k.1 = load i32, i32* %k
%n.1 = load i32, i32* %n
%temp.0 = icmp slt i32 %k.1, %n.1
br i1 %temp.0, label %for.body.0, label %for.exit.0

for.body.0:
%temp.1 = load i32*, i32** %arr
%k.2 = load i32, i32* %k
%arr.1 = getelementptr inbounds i32, i32* %temp.1, i32 %k.2
%call.read_int.1 = call i32 @read_int()
store i32 %call.read_int.1, i32* %arr.1
br label %for.hatch.0

for.hatch.0:
%k.3 = load i32, i32* %k
%temp.2 = add i32 %k.3, 1
store i32 %temp.2, i32* %k
br label %for.cond.0

for.exit.0:

br label %for.head.1
for.head.1:
%step = alloca i32
%step.0 = add i32 0, 0
store i32 %step.0, i32* %step
br label %for.cond.1

for.cond.1:
%step.1 = load i32, i32* %step
%n.2 = load i32, i32* %n
%temp.3 = sub i32 %n.2, 1
%temp.4 = icmp slt i32 %step.1, %temp.3
br i1 %temp.4, label %for.body.1, label %for.exit.1

for.body.1:

br label %for.head.2
for.head.2:
%i = alloca i32
%i.0 = add i32 0, 0
store i32 %i.0, i32* %i
br label %for.cond.2

for.cond.2:
%i.1 = load i32, i32* %i
%n.3 = load i32, i32* %n
%step.2 = load i32, i32* %step
%temp.5 = sub i32 %n.3, %step.2
%temp.6 = sub i32 %temp.5, 1
%temp.7 = icmp slt i32 %i.1, %temp.6
br i1 %temp.7, label %for.body.2, label %for.exit.2

for.body.2:
%temp.8 = load i32*, i32** %arr
%i.2 = load i32, i32* %i
%temp.9 = getelementptr inbounds i32, i32* %temp.8, i32 %i.2
%arr.2 = load i32, i32* %temp.9
%temp.10 = load i32*, i32** %arr
%i.3 = load i32, i32* %i
%temp.12 = add i32 %i.3, 1
%temp.11 = getelementptr inbounds i32, i32* %temp.10, i32 %temp.12
%arr.3 = load i32, i32* %temp.11
%temp.13 = icmp sgt i32 %arr.2, %arr.3
br i1 %temp.13, label %IfTrue.0, label %IfEnd.0

IfTrue.0:
%temp = alloca i32
%temp.14 = load i32*, i32** %arr
%i.4 = load i32, i32* %i
%temp.15 = getelementptr inbounds i32, i32* %temp.14, i32 %i.4
%arr.4 = load i32, i32* %temp.15
store i32 %arr.4, i32* %temp
%temp.16 = load i32*, i32** %arr
%i.5 = load i32, i32* %i
%arr.5 = getelementptr inbounds i32, i32* %temp.16, i32 %i.5
%temp.17 = load i32*, i32** %arr
%i.6 = load i32, i32* %i
%temp.19 = add i32 %i.6, 1
%temp.18 = getelementptr inbounds i32, i32* %temp.17, i32 %temp.19
%arr.6 = load i32, i32* %temp.18
store i32 %arr.6, i32* %arr.5
%temp.20 = load i32*, i32** %arr
%i.7 = load i32, i32* %i
%temp.21 = add i32 %i.7, 1
%arr.7 = getelementptr inbounds i32, i32* %temp.20, i32 %temp.21
%temp.22 = load i32, i32* %temp
store i32 %temp.22, i32* %arr.7
br label %IfEnd.0

IfEnd.0:
br label %for.hatch.2

for.hatch.2:
%i.8 = load i32, i32* %i
%temp.23 = add i32 %i.8, 1
store i32 %temp.23, i32* %i
br label %for.cond.2

for.exit.2:
br label %for.hatch.1

for.hatch.1:
%step.3 = load i32, i32* %step
%temp.24 = add i32 %step.3, 1
store i32 %temp.24, i32* %step
br label %for.cond.1

for.exit.1:

br label %for.head.3
for.head.3:
%j = alloca i32
%j.0 = add i32 0, 0
store i32 %j.0, i32* %j
br label %for.cond.3

for.cond.3:
%j.1 = load i32, i32* %j
%n.4 = load i32, i32* %n
%temp.25 = icmp slt i32 %j.1, %n.4
br i1 %temp.25, label %for.body.3, label %for.exit.3

for.body.3:
%temp.26 = load i32*, i32** %arr
%j.2 = load i32, i32* %j
%temp.27 = getelementptr inbounds i32, i32* %temp.26, i32 %j.2
%arr.8 = load i32, i32* %temp.27
call void @print_int(i32 %arr.8)
call void @print_char(i8 32)
br label %for.hatch.3

for.hatch.3:
%j.3 = load i32, i32* %j
%temp.28 = add i32 %j.3, 1
store i32 %temp.28, i32* %j
br label %for.cond.3

for.exit.3:
ret i32 0
}

define i32 @main () {
%call._main.0 = call i32 @_main()
ret i32 %call._main.0
}

