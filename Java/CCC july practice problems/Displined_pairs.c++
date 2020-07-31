#include <bits/stdc++.h> 
#define MAXN 1000005 
using namespace std; 
 
void mn( int arr[], int n, int nextBig[]) 
{ 
    stack<pair<int, int> > s; 

    for (int i = n - 1; i >= 0; i--) { 

        nextBig[i] = i; 
        while (!s.empty() && s.top().first < arr[i]) 
            s.pop(); 

        if (!s.empty()) 
            nextBig[i] = s.top().second; 

        s.push(pair<int, int>(arr[i], i)); 
    } 
} 
 
void mp(int arr[], int n, int prevBig[]) 
{ 
    stack<pair<int, int> > s; 
    for (int i = 0; i < n; i++) { 

        prevBig[i] = -1; 
        while (!s.empty() && s.top().first < arr[i]) 
            s.pop(); 

        if (!s.empty()) 
            prevBig[i] = s.top().second; 

        s.push(pair<int, int>(arr[i], i)); 
    } 
} 

int w(int a[], int n) 
{ 
    int nextBig[MAXN]; 
    int prevBig[MAXN]; 
    int maximum[MAXN]; 
    int ans = 0; 

     
    mp(a, n, prevBig); 


    mn(a, n, nextBig); 

    for (int i = 0; i < n; i++) 
        if (nextBig[i] != i) 
            maximum[nextBig[i] - i] = max(maximum[nextBig[i] - i], 
                                    i - prevBig[i]); 

    for (int i = 0; i < n; i++) 
        ans += maximum[i]; 

    return ans; 
} 


int main() 
{ 
    int n;
    cin>>n;
    int a[n];
    for(int i=0; i<n; i++)
    {
        cin>>a[i];
    }
    cout << w(a, n) << endl; 
    return 0; 
}