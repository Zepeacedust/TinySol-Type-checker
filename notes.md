# circular subtypes
consider the interfaces A and B
```
interface A<s> {
    method a((B, s) n);
}

interface B<s> {
    method a((A, s) n);
}
```
Whether or not they are subtypes of each other will recur infinitely.

An interface is a subtype of another if every component the supertype has a subtype in the subtype.

Is A a subtype of B?

consider A.a(), it is a subtype of B.a() if B is a subtype of A

But B is a subtype of A only if B.a() is a subtype of A.a().

Which is a subtype only if A is a subtype of B.

# Proposed fixes
## Making inheritance explicit


```
Interface A extends B {

}
```
## No inheritance
Just no interface inheritance.
This feels bad, but for now will be the option I will choose.

