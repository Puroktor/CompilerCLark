@_str0 = private unnamed_addr constant [5 x i8] c"Hello"
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


define i32 @get_str_size () {
ret i32 5
}

@size = global i32 0

define void @print_hello (i8* %parr, i32 %pn) {
%arr = alloca i8
store i8* %parr, i8* %arr
%n = alloca i32
store i32 %pn, i32* %n

br label %for.head.0
for.head.0:
%i = alloca i32
%i.0 = add i32 0, 0
store i32 %i.0, i32* %i
br label %for.cond.0

for.cond.0:
%i.1 = load i32, i32* %i
%n.0 = load i32, i32* %n
%temp.0 = icmp slt i32 %i.1, %n.0
br i1 %temp.0, label %for.body.0, label %for.exit.0

for.body.0:

br label %for.head.1
for.head.1:
%j = alloca i32
%j.0 = add i32 0, 0
store i32 %j.0, i32* %j
br label %for.cond.1

for.cond.1:
%j.1 = load i32, i32* %j
%size.0 = load i32, i32* @size
%temp.1 = icmp slt i32 %j.1, %size.0
br i1 %temp.1, label %for.body.1, label %for.exit.1

for.body.1:
%temp.2 = load i8*, i8** %arr
%j.2 = load i32, i32* %j
%temp.3 = getelementptr inbounds i8, i8* %temp.2, i32 %j.2
%arr.0 = load i8, i8* %temp.3
call void @print_char(i8 %arr.0)
br label %for.hatch.1

for.hatch.1:
%j.3 = load i32, i32* %j
%temp.4 = add i32 %j.3, 1
store i32 %temp.4, i32* %j
br label %for.cond.1

for.exit.1:
call void @print_char(i8 10)
br label %for.hatch.0

for.hatch.0:
%i.2 = load i32, i32* %i
%temp.5 = add i32 %i.2, 1
store i32 %temp.5, i32* %i
br label %for.cond.0

for.exit.0:
ret void
}


define i32 @_main () {
%size.1 = load i32, i32* @size
%str.0 = alloca i8, i32 %size.1
call void @llvm.memcpy.p0i8.p0i8.i32(i8* %str.0, i8* @_str0, i32 %size.1, i1 0)
%n = alloca i32
%call.read_int.0 = call i32 @read_int()
store i32 %call.read_int.0, i32* %n
%str.1 = getelementptr inbounds i8, i8* %str.0, i32 0
%n.1 = load i32, i32* %n
call void @print_hello(i8* %str.1, i32 %n.1)
ret i32 0
}

define i32 @main () {
%call.get_str_size.0 = call i32 @get_str_size()
store i32 %call.get_str_size.0, i32* @size
%call._main.0 = call i32 @_main()
ret i32 %call._main.0
}

