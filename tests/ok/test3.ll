@_str0 = private unnamed_addr constant [25 x i8] c"Enter Fibonacci number:  "
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


define i32 @fib (i32 %pn) {
%n = alloca i32
store i32 %pn, i32* %n
%n.0 = load i32, i32* %n
%temp.0 = icmp eq i32 %n.0, 1
%n.1 = load i32, i32* %n
%temp.1 = icmp eq i32 %n.1, 2
%temp.2 = or i1 %temp.0, %temp.1
br i1 %temp.2, label %IfTrue.0, label %IfEnd.0

IfTrue.0:
ret i32 1
br label %IfEnd.0

IfEnd.0:
%n.2 = load i32, i32* %n
%temp.3 = sub i32 %n.2, 1
%call.fib.0 = call i32 @fib(i32 %temp.3)
%n.3 = load i32, i32* %n
%temp.4 = sub i32 %n.3, 2
%call.fib.1 = call i32 @fib(i32 %temp.4)
%temp.5 = add i32 %call.fib.0, %call.fib.1
ret i32 %temp.5
}


define i32 @_main () {
%temp.6 = getelementptr inbounds i8, i8* @_str0, i32 0
call void @print_str(i8* %temp.6)
%n = alloca i32
%call.read_int.0 = call i32 @read_int()
store i32 %call.read_int.0, i32* %n
%number = alloca i32
%n.4 = load i32, i32* %n
%call.fib.2 = call i32 @fib(i32 %n.4)
store i32 %call.fib.2, i32* %number
%number.0 = load i32, i32* %number
call void @print_int(i32 %number.0)
ret i32 0
}

define i32 @main () {
%call._main.0 = call i32 @_main()
ret i32 %call._main.0
}

