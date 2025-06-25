Below are the top 10 questions and answers separated for each specified NumPy function. 
---

### array, zeros, ones

#### array Questions
1. How do you create a NumPy array from a Python list?
2. How can you create a 2D array from a list of lists?
3. How do you specify the data type of a NumPy array?
4. How can you check the shape of a created array?
5. How do you create an array with a specific order (e.g., Fortran)?
6. How can you create an array and initialize it with zeros?
7. How do you create an array from a range of numbers?
8. How can you copy an existing array to a new array?
9. How do you create an array with a custom step size?
10. How can you create an array with a specific dimension using arange?

#### array Answers
1. `np.array([1, 2, 3])`
2. `np.array([[1, 2], [3, 4]])`
3. `np.array([1, 2, 3], dtype=float)`
4. `arr = np.array([1, 2, 3]); arr.shape`
5. `np.array([1, 2, 3], order='F')`
6. `np.array([0, 0, 0])`
7. `np.array(range(5))`
8. `np.array(arr, copy=True)`
9. `np.array([i for i in range(0, 10, 2)])`
10. `np.array(np.arange(0, 10, 2).reshape(2, 5))`

#### zeros Questions
1. How do you create a 1D array of zeros with length 5?
2. How can you create a 3x3 matrix of zeros?
3. How do you specify the data type of a zeros array?
4. How can you check the size of a zeros array?
5. How do you create a zeros array with a specific order?
6. How can you reshape a zeros array into a 2D matrix?
7. How do you create a zeros array with a single column?
8. How can you fill a zeros array with a different value later?
9. How do you create a zeros array with a large dimension?
10. How can you use zeros to initialize a matrix for computation?

#### zeros Answers
1. `np.zeros(5)`
2. `np.zeros((3, 3))`
3. `np.zeros(5, dtype=int)`
4. `arr = np.zeros(5); arr.size`
5. `np.zeros(5, order='C')`
6. `np.zeros(9).reshape(3, 3)`
7. `np.zeros((5, 1))`
8. `arr = np.zeros(5); arr.fill(1)`
9. `np.zeros((1000, 1000))`
10. `matrix = np.zeros((3, 3)); matrix[0] = [1, 2, 3]`

#### ones Questions
1. How do you create a 1D array of ones with length 4?
2. How can you create a 2x2 matrix of ones?
3. How do you specify the data type of a ones array?
4. How can you check the dimensions of a ones array?
5. How do you create a ones array with a Fortran order?
6. How can you reshape a ones array into a different shape?
7. How do you create a ones array with a single row?
8. How can you multiply a ones array by a scalar?
9. How do you create a large ones array for testing?
10. How can you use ones to create a mask?

#### ones Answers
1. `np.ones(4)`
2. `np.ones((2, 2))`
3. `np.ones(4, dtype=float)`
4. `arr = np.ones((2, 2)); arr.ndim`
5. `np.ones(4, order='F')`
6. `np.ones(6).reshape(2, 3)`
7. `np.ones((1, 5))`
8. `arr = np.ones(5); arr * 2`
9. `np.ones((100, 100))`
10. `mask = np.ones(5, dtype=bool)`

---

### mean, std, sum

#### mean Questions
1. How do you calculate the mean of a 1D array?
2. How can you compute the mean along a specific axis of a 2D array?
3. How do you handle NaN values when calculating the mean?
4. How can you check the mean of a column in a 2D array?
5. How do you compute the mean with a specific dtype?
6. How can you calculate the mean of a subset of an array?
7. How do you use mean with a masked array?
8. How can you verify the mean calculation manually?
9. How do you compute the mean with weights?
10. How can you handle empty arrays with mean?

#### mean Answers
1. `np.mean(arr)`
2. `np.mean(arr, axis=0)`
3. `np.mean(arr, where=~np.isnan(arr))`
4. `np.mean(arr[:, 0])`
5. `np.mean(arr, dtype=float)`
6. `np.mean(arr[0:3])`
7. `np.mean(np.ma.masked_where(arr < 0, arr))`
8. `np.mean(arr); np.sum(arr) / len(arr)`
9. `np.average(arr, weights=[1, 2, 3])`
10. `np.mean(arr, out=np.array([0]), where=arr.size > 0)`

#### std Questions
1. How do you calculate the standard deviation of an array?
2. How can you compute the std along rows of a 2D array?
3. How do you set the degrees of freedom for std calculation?
4. How can you check the std of a specific column?
5. How do you handle NaN values in std?
6. How can you compute the std with a subset of data?
7. How do you use std with a masked array?
8. How can you compare std with manual calculation?
9. How do you compute the population std?
10. How can you set a default value for empty arrays in std?

#### std Answers
1. `np.std(arr)`
2. `np.std(arr, axis=1)`
3. `np.std(arr, ddof=1)`
4. `np.std(arr[:, 0])`
5. `np.std(arr, where=~np.isnan(arr))`
6. `np.std(arr[0:3])`
7. `np.std(np.ma.masked_where(arr < 0, arr))`
8. `np.std(arr); np.sqrt(np.mean((arr - np.mean(arr))**2))`
9. `np.std(arr, ddof=0)`
10. `np.std(arr, out=np.array([0]), where=arr.size > 0)`

#### sum Questions
1. How do you calculate the sum of a 1D array?
2. How can you sum along a specific axis of a 2D array?
3. How do you handle NaN values when summing?
4. How can you check the sum of a row in a 2D array?
5. How do you compute the sum with a specific dtype?
6. How can you sum a subset of an array?
7. How do you use sum with a masked array?
8. How can you verify the sum manually?
9. How do you compute the cumulative sum?
10. How can you set a default for empty arrays in sum?

#### sum Answers
1. `np.sum(arr)`
2. `np.sum(arr, axis=0)`
3. `np.sum(arr, where=~np.isnan(arr))`
4. `np.sum(arr[0, :])`
5. `np.sum(arr, dtype=int)`
6. `np.sum(arr[0:3])`
7. `np.sum(np.ma.masked_where(arr < 0, arr))`
8. `np.sum(arr); sum(arr.tolist())`
9. `np.cumsum(arr)`
10. `np.sum(arr, out=np.array([0]), where=arr.size > 0)`

---

### dot, matmul

#### dot Questions
1. How do you perform a dot product of two 1D arrays?
2. How can you compute the dot product of two 2D matrices?
3. How do you handle incompatible shapes in dot product?
4. How can you check the result of a dot product manually?
5. How do you use dot with a scalar and a vector?
6. How can you compute the dot product along a specific axis?
7. How do you use dot with a 3D array?
8. How can you verify the dot product using loops?
9. How do you handle NaN values in dot product?
10. How can you use dot to compute a matrix-vector product?

#### dot Answers
1. `np.dot(arr1, arr2)`
2. `np.dot(mat1, mat2)`
3. `try: np.dot(arr1, arr2); except ValueError: print("Incompatible shapes")`
4. `np.dot(arr1, arr2); sum(arr1 * arr2)`
5. `np.dot(2, arr)`
6. `np.dot(arr1, arr2, out=None)`
7. `np.dot(arr3d, arr2d)`
8. `result = 0; for i, j in zip(arr1, arr2): result += i * j`
9. `np.dot(np.nan_to_num(arr1), np.nan_to_num(arr2))`
10. `np.dot(mat, vec)`

#### matmul Questions
1. How do you perform matrix multiplication of two 2D arrays?
2. How can you use matmul with a 3D array and a 2D array?
3. How do you handle broadcasting in matmul?
4. How can you check the result of matmul manually?
5. How do you use matmul with a scalar?
6. How can you compute matmul along a specific axis?
7. How do you use matmul with a stack of matrices?
8. How can you verify matmul using dot?
9. How do you handle NaN values in matmul?
10. How can you use matmul for a batch matrix multiplication?

#### matmul Answers
1. `np.matmul(mat1, mat2)`
2. `np.matmul(arr3d, mat2d)`
3. `np.matmul(arr1[:, None], arr2[None, :])`
4. `np.matmul(mat1, mat2); np.dot(mat1, mat2)`
5. `np.matmul(2, mat)`
6. `np.matmul(arr1, arr2, axes=(0, 1))`
7. `np.matmul(stacked_mats, mat)`
8. `np.matmul(mat1, mat2); np.dot(mat1, mat2)`
9. `np.matmul(np.nan_to_num(mat1), np.nan_to_num(mat2))`
10. `np.matmul(batch_mats, mat)`

---

### random.rand, random.choice

#### random.rand Questions
1. How do you generate a 1D array of random numbers between 0 and 1?
2. How can you create a 2x3 matrix of random numbers?
3. How do you set a seed for reproducibility with random.rand?
4. How can you generate random numbers with a specific dtype?
5. How do you create a large random array for testing?
6. How can you scale random numbers to a specific range?
7. How do you generate random numbers with a specific shape?
8. How can you use random.rand with broadcasting?
9. How do you check the minimum value of random.rand output?
10. How can you generate random numbers and round them?

#### random.rand Answers
1. `np.random.rand(5)`
2. `np.random.rand(2, 3)`
3. `np.random.seed(42); np.random.rand(5)`
4. `np.random.rand(5, dtype=float32)`
5. `np.random.rand(1000, 1000)`
6. `np.random.rand(5) * 10`
7. `np.random.rand(2, 2, 2)`
8. `np.random.rand(2, 1) + np.random.rand(1, 3)`
9. `np.min(np.random.rand(5))`
10. `np.round(np.random.rand(5), 2)`

#### random.choice Questions
1. How do you randomly select an element from a list?
2. How can you select multiple elements without replacement?
3. How do you set a seed for random.choice?
4. How can you select with replacement from an array?
5. How do you specify the size of the output array in random.choice?
6. How can you use random.choice with probabilities?
7. How do you select from a range of numbers?
8. How can you check the uniqueness of selected elements?
9. How do you use random.choice with a 2D array?
10. How can you generate a random sample with a specific axis?

#### random.choice Answers
1. `np.random.choice([1, 2, 3])`
2. `np.random.choice([1, 2, 3], size=2, replace=False)`
3. `np.random.seed(42); np.random.choice([1, 2, 3])`
4. `np.random.choice([1, 2, 3], size=2, replace=True)`
5. `np.random.choice([1, 2, 3], size=(2, 2))`
6. `np.random.choice([1, 2, 3], p=[0.5, 0.3, 0.2])`
7. `np.random.choice(5, size=3)`
8. `len(np.unique(np.random.choice(5, size=3, replace=False))) == 3`
9. `np.random.choice(arr2d.flatten(), size=3)`
10. `np.random.choice(arr, size=3, axis=0)`

---

### eig

#### eig Questions
1. How do you compute the eigenvalues of a square matrix?
2. How can you get both eigenvalues and eigenvectors?
3. How do you check the shape of the eigenvector matrix?
4. How can you verify the eigenvalue equation manually?
5. How do you use eig with a symmetric matrix?
6. How can you handle a non-square matrix with eig?
7. How do you compute the condition number using eig?
8. How can you sort eigenvalues in descending order?
9. How do you use eig with a complex matrix?
10. How can you check the orthogonality of eigenvectors?

#### eig Answers
1. `np.linalg.eigvals(mat)`
2. `eigenvals, eigenvecs = np.linalg.eig(mat)`
3. `eigenvecs.shape`
4. `np.allclose(np.dot(mat, eigenvecs[:, 0]), eigenvals[0] * eigenvecs[:, 0])`
5. `np.linalg.eig(np.array([[1, 0], [0, 1]]))`
6. `try: np.linalg.eig(mat); except np.linalg.LinAlgError: print("Not square")`
7. `np.linalg.cond(mat, p='fro')`
8. `idx = np.argsort(eigenvals)[::-1]; eigenvals = eigenvals[idx]`
9. `np.linalg.eig(np.array([[0, -1], [1, 0]]))`
10. `np.allclose(np.dot(eigenvecs.T, eigenvecs), np.eye(len(eigenvecs)))`

---

### where, percentile, linspace

#### where Questions
1. How do you replace values in an array based on a condition?
2. How can you get the indices where a condition is true?
3. How do you use where with multiple conditions?
4. How can you replace values with different outputs?
5. How do you apply where to a 2D array?
6. How can you count occurrences using where?
7. How do you use where with NaN values?
8. How can you modify an array in place with where?
9. How do you use where with a logical OR condition?
10. How can you extract elements based on where?

#### where Answers
1. `np.where(arr > 0, arr, 0)`
2. `np.where(arr > 0)`
3. `np.where((arr > 0) & (arr < 5), arr, 0)`
4. `np.where(arr > 0, 1, -1)`
5. `np.where(arr2d > 0, arr2d, 0)`
6. `np.sum(np.where(arr > 0, 1, 0))`
7. `np.where(np.isnan(arr), 0, arr)`
8. `arr[:] = np.where(arr > 0, arr, 0)`
9. `np.where((arr > 0) | (arr < -5), arr, 0)`
10. `arr[np.where(arr > 0)]`

#### percentile Questions
1. How do you calculate the 50th percentile of an array?
2. How can you compute percentiles along a specific axis?
3. How do you handle NaN values in percentile?
4. How can you get multiple percentiles at once?
5. How do you use percentile with interpolation?
6. How can you check the percentile of a specific value?
7. How do you compute percentiles for a 2D array?
8. How can you set the method for percentile calculation?
9. How do you use percentile with a masked array?
10. How can you verify percentile results manually?

#### percentile Answers
1. `np.percentile(arr, 50)`
2. `np.percentile(arr, 50, axis=0)`
3. `np.percentile(arr, 50, where=~np.isnan(arr))`
4. `np.percentile(arr, [25, 50, 75])`
5. `np.percentile(arr, 50, interpolation='linear')`
6. `np.percentile(arr, np.searchsorted(np.percentile(arr, [0, 100]), value))`
7. `np.percentile(arr2d, 50, axis=1)`
8. `np.percentile(arr, 50, method='averaged_inverted_cdf')`
9. `np.percentile(np.ma.masked_where(arr < 0, arr), 50)`
10. `np.percentile(arr, 50); np.sort(arr)[len(arr)//2]`

#### linspace Questions
1. How do you create an array with 5 evenly spaced numbers from 0 to 10?
2. How can you exclude the endpoint in linspace?
3. How do you specify the number of points in linspace?
4. How can you create a linspace array with float dtype?
5. How do you use linspace with a negative range?
6. How can you check the step size of linspace?
7. How do you create a 2D array using linspace?
8. How can you use linspace for plotting purposes?
9. How do you set the precision of linspace values?
10. How can you generate linspace with a specific axis?

#### linspace Answers
1. `np.linspace(0, 10, 5)`
2. `np.linspace(0, 10, 5, endpoint=False)`
3. `np.linspace(0, 10, num=5)`
4. `np.linspace(0, 10, 5, dtype=float)`
5. `np.linspace(-5, 5, 5)`
6. `(np.linspace(0, 10, 5)[1] - np.linspace(0, 10, 5)[0])`
7. `np.linspace(0, 10, 5).reshape(1, 5)`
8. `x = np.linspace(0, 10, 100); plt.plot(x, np.sin(x))`
9. `np.linspace(0, 10, 5, endpoint=True, retstep=True)`
10. `np.linspace(0, 10, 5, axis=0)`

---

### corrcoef, linalg.norm, unique

#### corrcoef Questions
1. How do you compute the correlation coefficient matrix for two arrays?
2. How can you calculate the correlation for a 2D array?
3. How do you handle NaN values in corrcoef?
4. How can you extract the correlation between specific columns?
5. How do you verify corrcoef results manually?
6. How can you use corrcoef with a masked array?
7. How do you compute the Pearson correlation only?
8. How can you check the shape of the corrcoef output?
9. How do you use corrcoef with a large dataset?
10. How can you set a threshold for significant correlation?

#### corrcoef Answers
1. `np.corrcoef(arr1, arr2)`
2. `np.corrcoef(arr2d)`
3. `np.corrcoef(np.nan_to_num(arr1), np.nan_to_num(arr2))`
4. `np.corrcoef(arr2d)[0, 1]`
5. `np.corrcoef(arr1, arr2); np.cov(arr1, arr2) / (np.std(arr1) * np.std(arr2))`
6. `np.corrcoef(np.ma.masked_where(arr < 0, arr))`
7. `np.corrcoef(arr1, arr2, rowvar=False)`
8. `np.corrcoef(arr1, arr2).shape`
9. `np.corrcoef(arr2d[:1000])`
10. `corr = np.corrcoef(arr1, arr2); corr[corr < 0.5] = 0`

#### linalg.norm Questions
1. How do you compute the L2 norm of a vector?
2. How can you calculate the norm of a matrix?
3. How do you specify a different norm (e.g., L1)?
4. How can you compute the norm along a specific axis?
5. How do you handle NaN values in linalg.norm?
6. How can you verify the norm calculation manually?
7. How do you use linalg.norm with a 3D array?
8. How can you set the ord parameter for matrix norm?
9. How do you compute the Frobenius norm?
10. How can you use linalg.norm to normalize a vector?

#### linalg.norm Answers
1. `np.linalg.norm(vec)`
2. `np.linalg.norm(mat)`
3. `np.linalg.norm(vec, ord=1)`
4. `np.linalg.norm(arr, axis=0)`
5. `np.linalg.norm(np.nan_to_num(arr))`
6. `np.linalg.norm(vec); np.sqrt(np.sum(vec**2))`
7. `np.linalg.norm(arr3d, axis=(1, 2))`
8. `np.linalg.norm(mat, ord='fro')`
9. `np.linalg.norm(mat, ord='fro')`
10. `vec / np.linalg.norm(vec)`

#### unique Questions
1. How do you find unique elements in an array?
2. How can you get the counts of unique elements?
3. How do you use unique with a sorted output?
4. How can you find unique rows in a 2D array?
5. How do you handle NaN values in unique?
6. How can you get the indices of unique elements?
7. How do you use unique with a specific axis?
8. How can you verify the uniqueness manually?
9. How do you use unique with a large array?
10. How can you return the inverse indices with unique?

#### unique Answers
1. `np.unique(arr)`
2. `np.unique(arr, return_counts=True)`
3. `np.unique(arr, return_index=True)`
4. `np.unique(arr2d, axis=0)`
5. `np.unique(np.nan_to_num(arr))`
6. `np.unique(arr, return_index=True)[1]`
7. `np.unique(arr2d, axis=1)`
8. `len(np.unique(arr)) == len(set(arr))`
9. `np.unique(arr[:1000])`
10. `np.unique(arr, return_inverse=True)[1]`
