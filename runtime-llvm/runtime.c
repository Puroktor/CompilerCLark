#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>

void print_str(char str[])
{
    printf("%s", str);
}

void print_char(char ch)
{
    printf("%c", ch);
}

char read_char()
{
    char ch;
    scanf("%c", &ch);
    return ch;
}

void print_int(int i)
{
    printf("%d", i);
}

int read_int()
{
    int i;
    scanf("%d", &i);
    return i;
}

void print_double(double d)
{
    printf("%lf", d);
}

double read_double()
{
    double d;
    scanf("%lf", &d);
    return d;
}