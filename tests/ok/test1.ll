@_str0 = private unnamed_addr constant [13 x i8] c"Hello world! "
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
%temp.0 = getelementptr inbounds i8, i8* @_str0, i8 0
call void @print_str(i8* %temp.0)
ret i32 0
}

define i32 @main () {
%call._main.0 = call i32 @_main()
ret i32 %call._main.0
}

