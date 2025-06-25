Below are the questions and answers separated for each specified Seaborn function. This format is designed to help Sandhya Rani Rathlavath, with her data analysis background, prepare effectively for her Nextracker interview by practicing questions independently before checking the answers. The examples assume a typical dataset context, and the current date and time (11:21 PM IST, Wednesday, June 25, 2025) are considered where relevant.

---

### histplot, boxplot

#### histplot Questions
1. How do you create a histogram of the 'age' column in a DataFrame?
2. How can you add a kernel density estimate to a histogram?
3. How do you set the number of bins in a histogram?
4. How can you color a histogram by a categorical variable like 'gender'?
5. How do you save a histogram plot to a file?

#### histplot Answers
1. `sns.histplot(data=df, x='age')`
2. `sns.histplot(data=df, x='age', kde=True)`
3. `sns.histplot(data=df, x='age', bins=20)`
4. `sns.histplot(data=df, x='age', hue='gender')`
5. `sns.histplot(data=df, x='age').figure.savefig('histogram.png')`

#### boxplot Questions
1. How do you create a boxplot for the 'salary' column?
2. How can you create a boxplot with 'department' on the x-axis?
3. How do you add a hue parameter to differentiate by 'region'?
4. How can you set the width of the boxplot boxes?
5. How do you display the data points on a boxplot?

#### boxplot Answers
1. `sns.boxplot(data=df, y='salary')`
2. `sns.boxplot(data=df, x='department', y='salary')`
3. `sns.boxplot(data=df, x='department', y='salary', hue='region')`
4. `sns.boxplot(data=df, x='department', y='salary', width=0.5)`
5. `sns.boxplot(data=df, x='department', y='salary', showfliers=True)`

---

### scatterplot, pairplot

#### scatterplot Questions
1. How do you create a scatter plot of 'age' vs 'salary'?
2. How can you color points by a categorical variable like 'department'?
3. How do you add a regression line to a scatter plot?
4. How can you adjust the size of points based on 'experience'?
5. How do you set a custom marker style for the scatter plot?

#### scatterplot Answers
1. `sns.scatterplot(data=df, x='age', y='salary')`
2. `sns.scatterplot(data=df, x='age', y='salary', hue='department')`
3. `sns.scatterplot(data=df, x='age', y='salary', ci=None)`
4. `sns.scatterplot(data=df, x='age', y='salary', size='experience')`
5. `sns.scatterplot(data=df, x='age', y='salary', marker='^')`

#### pairplot Questions
1. How do you create a pairplot for all numeric columns in a DataFrame?
2. How can you color the pairplot by a 'gender' variable?
3. How do you include only specific columns in a pairplot?
4. How can you add a kernel density diagonal in a pairplot?
5. How do you save a pairplot to a file?

#### pairplot Answers
1. `sns.pairplot(data=df)`
2. `sns.pairplot(data=df, hue='gender')`
3. `sns.pairplot(data=df, vars=['age', 'salary', 'experience'])`
4. `sns.pairplot(data=df, diag_kind='kde')`
5. `sns.pairplot(data=df).savefig('pairplot.png')`

---

### catplot, barplot

#### catplot Questions
1. How do you create a categorical scatter plot for 'salary' by 'department'?
2. How can you use 'swarm' kind with a hue for 'region'?
3. How do you set the height and aspect ratio of a catplot?
4. How can you create a boxplot using catplot with a specific order?
5. How do you add a title to a catplot?

#### catplot Answers
1. `sns.catplot(data=df, x='department', y='salary', kind='strip')`
2. `sns.catplot(data=df, x='department', y='salary', hue='region', kind='swarm')`
3. `sns.catplot(data=df, x='department', y='salary', height=6, aspect=1.5)`
4. `sns.catplot(data=df, x='department', y='salary', kind='box', order=['HR', 'IT', 'Sales'])`
5. `sns.catplot(data=df, x='department', y='salary').set(title='Salary by Department')`

#### barplot Questions
1. How do you create a bar plot of average 'salary' by 'department'?
2. How can you add error bars to a barplot?
3. How do you color bars by a 'region' variable?
4. How can you set a custom palette for a barplot?
5. How do you rotate x-axis labels in a barplot?

#### barplot Answers
1. `sns.barplot(data=df, x='department', y='salary', estimator=np.mean)`
2. `sns.barplot(data=df, x='department', y='salary', ci=95)`
3. `sns.barplot(data=df, x='department', y='salary', hue='region')`
4. `sns.barplot(data=df, x='department', y='salary', palette='Blues')`
5. `sns.barplot(data=df, x='department', y='salary').tick_params(axis='x', rotation=45)`

---

### heatmap

#### heatmap Questions
1. How do you create a heatmap of a correlation matrix?
2. How can you annotate values in a heatmap?
3. How do you set a custom color map for a heatmap?
4. How can you adjust the figure size of a heatmap?
5. How do you save a heatmap to a file?

#### heatmap Answers
1. `sns.heatmap(data=df.corr(), annot=False)`
2. `sns.heatmap(data=df.corr(), annot=True, fmt='.2f')`
3. `sns.heatmap(data=df.corr(), cmap='YlOrRd')`
4. `plt.figure(figsize=(10, 8)); sns.heatmap(data=df.corr())`
5. `sns.heatmap(data=df.corr()).figure.savefig('heatmap.png')`

---

### kdeplot, contourf

#### kdeplot Questions
1. How do you create a kernel density plot for the 'salary' column?
2. How can you overlay a KDE plot for 'salary' by 'gender'?
3. How do you set the bandwidth for a KDE plot?
4. How can you create a 2D KDE plot for 'age' and 'salary'?
5. How do you add a fill under the KDE curve?

#### kdeplot Answers
1. `sns.kdeplot(data=df, x='salary')`
2. `sns.kdeplot(data=df, x='salary', hue='gender')`
3. `sns.kdeplot(data=df, x='salary', bw_adjust=0.5)`
4. `sns.kdeplot(data=df, x='age', y='salary')`
5. `sns.kdeplot(data=df, x='salary', fill=True)`

#### contourf Questions
1. How do you create a filled contour plot for 'age' and 'salary'?
2. How can you set the number of contour levels?
3. How do you add a colorbar to a contourf plot?
4. How can you adjust the transparency of a contourf plot?
5. How do you limit the contourf plot to a specific range?

#### contourf Answers
1. `sns.kdeplot(data=df, x='age', y='salary', fill=True, thresh=0)`
2. `sns.kdeplot(data=df, x='age', y='salary', levels=10, fill=True)`
3. `sns.kdeplot(data=df, x='age', y='salary', fill=True, cbar=True)`
4. `sns.kdeplot(data=df, x='age', y='salary', fill=True, alpha=0.5)`
5. `sns.kdeplot(data=df, x='age', y='salary', fill=True, vmin=0, vmax=1)`

---

### violinplot, swarmplot

#### violinplot Questions
1. How do you create a violin plot for 'salary' by 'department'?
2. How can you split the violin plot by 'region'?
3. How do you set the width of the violin plots?
4. How can you add a title to a violin plot?
5. How do you display inner quartiles in a violin plot?

#### violinplot Answers
1. `sns.violinplot(data=df, x='department', y='salary')`
2. `sns.violinplot(data=df, x='department', y='salary', hue='region', split=True)`
3. `sns.violinplot(data=df, x='department', y='salary', width=0.8)`
4. `sns.violinplot(data=df, x='department', y='salary').set(title='Salary Distribution')`
5. `sns.violinplot(data=df, x='department', y='salary', inner='quartile')`

#### swarmplot Questions
1. How do you create a swarm plot for 'salary' by 'department'?
2. How can you color points by 'region' in a swarm plot?
3. How do you adjust the size of points in a swarm plot?
4. How can you set a custom palette for a swarm plot?
5. How do you combine a swarm plot with a boxplot?

#### swarmplot Answers
1. `sns.swarmplot(data=df, x='department', y='salary')`
2. `sns.swarmplot(data=df, x='department', y='salary', hue='region')`
3. `sns.swarmplot(data=df, x='department', y='salary', size=8)`
4. `sns.swarmplot(data=df, x='department', y='salary', palette='Set2')`
5. `sns.boxplot(data=df, x='department', y='salary'); sns.swarmplot(data=df, x='department', y='salary', color='black')`

---

### jointplot, relplot

#### jointplot Questions
1. How do you create a joint plot for 'age' and 'salary'?
2. How can you use a hexbin plot in a joint plot?
3. How do you add a regression line to a joint plot?
4. How can you set the color by 'department' in a joint plot?
5. How do you save a joint plot to a file?

#### jointplot Answers
1. `sns.jointplot(data=df, x='age', y='salary')`
2. `sns.jointplot(data=df, x='age', y='salary', kind='hex')`
3. `sns.jointplot(data=df, x='age', y='salary', kind='reg')`
4. `sns.jointplot(data=df, x='age', y='salary', hue='department')`
5. `sns.jointplot(data=df, x='age', y='salary').savefig('jointplot.png')`

#### relplot Questions
1. How do you create a relational plot of 'age' vs 'salary'?
2. How can you use 'line' kind with 'department' as hue?
3. How do you set the size of points based on 'experience'?
4. How can you adjust the height and aspect of a relplot?
5. How do you add a facet grid by 'region'?

#### relplot Answers
1. `sns.relplot(data=df, x='age', y='salary')`
2. `sns.relplot(data=df, x='age', y='salary', hue='department', kind='line')`
3. `sns.relplot(data=df, x='age', y='salary', size='experience')`
4. `sns.relplot(data=df, x='age', y='salary', height=6, aspect=1.5)`
5. `sns.relplot(data=df, x='age', y='salary', col='region')`

---

This structure allows Sandhya to practice Seaborn visualization techniques by attempting the questions first and then verifying with the answers, enhancing her data visualization skills for the interview.