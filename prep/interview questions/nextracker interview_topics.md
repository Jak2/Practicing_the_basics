
### Skill-Wise Specific Functions and Preparation

#### SQL
- SELECT, WHERE, ORDER BY, GROUP BY, HAVING
- JOIN, INNER, LEFT, RIGHT, FULL
- COUNT, SUM, AVG, MIN, MAX
- ROW_NUMBER, RANK, LAG, LEAD
- CASE, COALESCE
- PIVOT, UNPIVOT, EXPLAIN
- WITH, OVER, PARTITION BY
- STRING_AGG, JSON_QUERY, TRY_CAST

#### Pandas
- read_csv, to_csv
- groupby, agg
- merge, concat
- fillna, dropna, replace
- resample, rolling
- melt, pivot
- apply, map, cut
- to_datetime, diff, shift

#### Seaborn
- histplot, boxplot
- scatterplot, pairplot
- catplot, barplot
- heatmap
- kdeplot, contourf
- violinplot, swarmplot
- jointplot, relplot

#### Matplotlib
- plot, scatter, bar
- subplot, figure
- title, xlabel, ylabel, legend
- annotate, text
- grid, twinx, colorbar
- savefig, tight_layout, loglog

#### Streamlit
- st.write, st.dataframe
- st.selectbox, st.slider
- st.plotly_chart
- st.cache_data
- st.file_uploader, st.session_state
- st.sidebar, st.form
- st.image, st.download_button

#### NumPy
- array, zeros, ones
- mean, std, sum
- dot, matmul
- random.rand, random.choice
- eig
- where, percentile, linspace
- corrcoef, linalg.norm, unique

#### Plotly
- go.Scatter, go.Bar
- px.line, px.histogram
- go.Layout
- add_trace, update_traces
- go.Pie, go.Heatmap
- go.Box, px.scatter_3d
- go.FigureWidget, px.choropleth

### Rationale
- **SQL**: Added WITH for CTEs, OVER/PARTITION BY for advanced windowing, and STRING_AGG/JSON_QUERY/TRY_CAST for text and JSON handling, reflecting complex data integration from her BI work.
- **Pandas**: Included apply/map/cut for custom operations, to_datetime/diff/shift for time-series analysis, aligning with her automation and analytics experience.
- **Seaborn**: Added violinplot/swarmplot for detailed distributions, jointplot/relplot for multivariate analysis, enhancing her dashboard insights.
- **Matplotlib**: Included grid/twinx/colorbar for advanced layouts, savefig/tight_layout/loglog for professional outputs, supporting her reporting skills.
- **Streamlit**: Added st.sidebar/st.form for structured inputs, st.image/st.download_button for rich outputs, meeting interactive app trends.
- **NumPy**: Included where/percentile/linspace for conditional operations, corrcoef/linalg.norm/unique for statistical and linear algebra depth, relevant to her Python scripts.
- **Plotly**: Added go.Box/px.scatter_3d for advanced visuals, go.FigureWidget for interactivity, px.choropleth for geographic data, aligning with modern visualization demands.

### Sufficiency
This expanded list should now cover a wide variety of topics, from basic to advanced, suitable for a 2.5+ year experienced candidate. It addresses potential questions on niche scenarios (e.g., 3D plots, JSON data) and trending areas (e.g., interactive widgets, geospatial analysis). Practice these with Nextracker-relevant datasets (e.g., solar panel performance, maintenance logs) to solidify her expertise.