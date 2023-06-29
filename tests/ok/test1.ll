declare i32 @read_int()
declare double @read_double()
declare i8 @read_char()
declare void @print_int(i32)
declare void @print_double(double)
declare void @print_char(i8)
declare void @llvm.memcpy.p0i32.p0i32.i32(i32*, i32*, i32, i1)
declare void @llvm.memcpy.p0i1.p0i1.i32(i1*, i1*, i32, i1)
declare void @llvm.memcpy.p0i8.p0i8.i32(i8*, i8*, i32, i1)
declare void @llvm.memcpy.p0double.p0double.i32(double*, double*, i32, i1)

define void @print_hello (i32 %cn) {

%n = alloca i32
store i32 %cn, i32* %n
%arr.0 = alloca i8, i32 5
%arr = alloca i8*
store i8* %arr.0, i8** %arr
%temp.0 = load i8*, i8** %arr
%arr.1 = getelementptr inbounds i8, i8* %temp.0, i32 0
%arr.2 = add i8 0, 72
store i8 %arr.2, i8* %arr.1
%temp.1 = load i8*, i8** %arr
%arr.3 = getelementptr inbounds i8, i8* %temp.1, i32 1
%arr.4 = add i8 0, 101
store i8 %arr.4, i8* %arr.3
%temp.2 = load i8*, i8** %arr
%arr.5 = getelementptr inbounds i8, i8* %temp.2, i32 2
%arr.6 = add i8 0, 108
store i8 %arr.6, i8* %arr.5
%temp.3 = load i8*, i8** %arr
%arr.7 = getelementptr inbounds i8, i8* %temp.3, i32 3
%arr.8 = add i8 0, 108
store i8 %arr.8, i8* %arr.7
%temp.4 = load i8*, i8** %arr
%arr.9 = getelementptr inbounds i8, i8* %temp.4, i32 4
%arr.10 = add i8 0, 111
store i8 %arr.10, i8* %arr.9

br label %for.head.0
for.head.0:
%i = alloca i32
%i.0 = add i32 0, 0
store i32 %i.0, i32* %i
br label %for.cond.0

for.cond.0:
%i.1 = load i32, i32* %i
%n.0 = load i32, i32* %n
%temp.5 = icmp slt i32 %i.1, %n.0
br i1 %temp.5, label %for.body.0, label %for.exit.0

for.body.0:

br label %for.head.1
for.head.1:
%j = alloca i32
%j.0 = add i32 0, 0
store i32 %j.0, i32* %j
br label %for.cond.1

for.cond.1:
%j.1 = load i32, i32* %j
%temp.6 = icmp slt i32 %j.1, 5
br i1 %temp.6, label %for.body.1, label %for.exit.1

for.body.1:
%temp.7 = load i8*, i8** %arr
%j.2 = load i32, i32* %j
%temp.8 = getelementptr inbounds i8, i8* %temp.7, i32 %j.2
%arr.11 = load i8, i8* %temp.8
call void @print_char(i8 %arr.11)
br label %for.hatch.1

for.hatch.1:
%j.3 = load i32, i32* %j
%temp.9 = add i32 %j.3, 1
store i32 %temp.9, i32* %j
br label %for.cond.1

for.exit.1:
call void @print_char(i8 10)
br label %for.hatch.0

for.hatch.0:
%i.2 = load i32, i32* %i
%temp.10 = add i32 %i.2, 1
store i32 %temp.10, i32* %i
br label %for.cond.0

for.exit.0:
ret void
}

define i32 @main () {

%n = alloca i32
%call.read_int.0 = call i32 @read_int()
store i32 %call.read_int.0, i32* %n
%n.1 = load i32, i32* %n
call void @print_hello(i32 %n.1)
ret i32 0
}


