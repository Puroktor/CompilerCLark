declare i32 @printf(i8*, ...) nounwind
declare i32 @scanf(i8*, ...) nounwind

declare void @llvm.memcpy.p0i32.p0i32.i32(i32*, i32*, i32, i1)
declare void @llvm.memcpy.p0i1.p0i1.i32(i1*, i1*, i32, i1)
declare void @llvm.memcpy.p0i8.p0i8.i32(i8*, i8*, i32, i1)
declare void @llvm.memcpy.p0double.p0double.i32(double*, double*, i32, i1)

@int.0.0 = global i32 0
@char.0.0 = global i8 0
@double.0.0 = global double 0.0

@formatInt = private constant [3 x i8] c"%d\00"
@formatDouble = private constant [3 x i8] c"%f\00"
@formatChar = private constant [3 x i8] c"%c\00"

define void @main () {

%n = alloca i32
%n.0 = add i32 0, 5
store i32 %n.0, i32* %n
%n.1 = load i32, i32* %n
%arr.0 = alloca i8, i32 %n.1
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
%temp.5 = icmp slt i32 %i.1, 5
br i1 %temp.5, label %for.body.0, label %for.exit.0

for.body.0:
%temp.6 = load i8*, i8** %arr
%i.2 = load i32, i32* %i
%temp.7 = getelementptr inbounds i8, i8* %temp.6, i32 %i.2
%arr.11 = load i8, i8* %temp.7
%call.print_char.0 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @formatChar, i32 0, i32 0), i8 %arr.11)
br label %for.hatch.0


for.hatch.0:
%i.3 = load i32, i32* %i
%temp.8 = add i32 %i.3, 1
store i32 %temp.8, i32* %i
br label %for.cond.0

for.exit.0:
%a = alloca i32
call i32 (i8*, ...) @scanf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @formatChar, i32 0, i32 0), i8* @char.0.0)
%call.read_char.0 = load i8, i8* @char.0.0
%temp.9 = zext i8 %call.read_char.0 to i32
store i32 %temp.9, i32* %a
ret void
}

