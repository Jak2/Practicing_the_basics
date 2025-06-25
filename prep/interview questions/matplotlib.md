Below are the questions and answers separated for each specified Matplotlib function. 
---

### plot, scatter, bar

#### plot Questions
1. How do you create a simple line plot with x and y data?
2. How can you set a custom color and linestyle for a line plot?
3. How do you plot multiple lines on the same figure?
4. How can you add markers to a line plot?
5. How do you set a label for a line plot to use in a legend?

#### plot Answers
1. `plt.plot(x, y)`
2. `plt.plot(x, y, color='red', linestyle='--')`
3. `plt.plot(x1, y1); plt.plot(x2, y2)`
4. `plt.plot(x, y, marker='o')`
5. `plt.plot(x, y, label='Data')`

#### scatter Questions
1. How do you create a scatter plot with x and y coordinates?
2. How can you vary the size of points based on a third variable?
3. How do you set different colors for points using a colormap?
4. How can you adjust the transparency of scatter points?
5. How do you add a title to a scatter plot?

#### scatter Answers
1. `plt.scatter(x, y)`
2. `plt.scatter(x, y, s=size)`
3. `plt.scatter(x, y, c=values, cmap='viridis')`
4. `plt.scatter(x, y, alpha=0.5)`
5. `plt.scatter(x, y); plt.title('Scatter Plot')`

#### bar Questions
1. How do you create a bar plot with categorical x-values and heights?
2. How can you set different colors for each bar?
3. How do you create a grouped bar plot with multiple datasets?
4. How can you add error bars to a bar plot?
5. How do you rotate x-axis labels in a bar plot?

#### bar Answers
1. `plt.bar(x, height)`
2. `plt.bar(x, height, color=['red', 'blue', 'green'])`
3. `plt.bar(x - 0.2, height1, width=0.4); plt.bar(x + 0.2, height2, width=0.4)`
4. `plt.bar(x, height, yerr=error)`
5. `plt.bar(x, height); plt.xticks(rotation=45)`

---

### subplot, figure

#### subplot Questions
1. How do you create a 2x2 grid of subplots?
2. How can you plot data in the first subplot of a 1x2 grid?
3. How do you adjust the spacing between subplots?
4. How can you set a title for a specific subplot?
5. How do you share the x-axis across subplots?

#### subplot Answers
1. `plt.subplot(2, 2, 1)`
2. `plt.subplot(1, 2, 1); plt.plot(x, y)`
3. `plt.tight_layout()`
4. `plt.subplot(1, 2, 1); plt.plot(x, y); plt.title('Plot 1')`
5. `plt.subplot(2, 1, 1, sharex=plt.subplot(2, 1, 2)); plt.plot(x, y)`

#### figure Questions
1. How do you create a new figure with a specific size?
2. How can you set the background color of a figure?
3. How do you add a title to an entire figure?
4. How can you create multiple figures in a script?
5. How do you adjust the DPI of a figure?

#### figure Answers
1. `plt.figure(figsize=(10, 6))`
2. `plt.figure(facecolor='lightgray')`
3. `plt.figure(); plt.suptitle('Main Title')`
4. `plt.figure(1); plt.plot(x1, y1); plt.figure(2); plt.plot(x2, y2)`
5. `plt.figure(dpi=100)`

---

### title, xlabel, ylabel, legend

#### title Questions
1. How do you add a title to a plot?
2. How can you set a custom font size for the title?
3. How do you center the title horizontally?
4. How can you add a title with a specific color?
5. How do you adjust the vertical position of the title?

#### title Answers
1. `plt.title('My Plot')`
2. `plt.title('My Plot', fontsize=14)`
3. `plt.title('My Plot', loc='center')`
4. `plt.title('My Plot', color='blue')`
5. `plt.title('My Plot', pad=20)`

#### xlabel Questions
1. How do you label the x-axis of a plot?
2. How can you set a custom font size for the x-axis label?
3. How do you rotate the x-axis label?
4. How can you add a label with a specific color?
5. How do you adjust the position of the x-axis label?

#### xlabel Answers
1. `plt.xlabel('X Axis')`
2. `plt.xlabel('X Axis', fontsize=12)`
3. `plt.xlabel('X Axis', rotation=45)`
4. `plt.xlabel('X Axis', color='green')`
5. `plt.xlabel('X Axis', labelpad=10)`

#### ylabel Questions
1. How do you label the y-axis of a plot?
2. How can you set a custom font size for the y-axis label?
3. How do you rotate the y-axis label?
4. How can you add a label with a specific color?
5. How do you adjust the position of the y-axis label?

#### ylabel Answers
1. `plt.ylabel('Y Axis')`
2. `plt.ylabel('Y Axis', fontsize=12)`
3. `plt.ylabel('Y Axis', rotation=0)`
4. `plt.ylabel('Y Axis', color='red')`
5. `plt.ylabel('Y Axis', labelpad=10)`

#### legend Questions
1. How do you add a legend to a plot with labeled lines?
2. How can you set a custom location for the legend?
3. How do you adjust the font size of the legend?
4. How can you add a title to the legend?
5. How do you make the legend box transparent?

#### legend Answers
1. `plt.plot(x, y, label='Line'); plt.legend()`
2. `plt.legend(loc='upper right')`
3. `plt.legend(fontsize=12)`
4. `plt.legend(title='Legend Title')`
5. `plt.legend(framealpha=0.5)`

---

### annotate, text

#### annotate Questions
1. How do you add an annotation with an arrow to a point?
2. How can you set a custom color for an annotation?
3. How do you adjust the arrow style in an annotation?
4. How can you specify the coordinates for an annotation?
5. How do you add multiple annotations to a plot?

#### annotate Answers
1. `plt.annotate('Point', xy=(2, 10), xytext=(3, 15), arrowprops=dict(facecolor='black'))`
2. `plt.annotate('Point', xy=(2, 10), xytext=(3, 15), color='red')`
3. `plt.annotate('Point', xy=(2, 10), xytext=(3, 15), arrowprops=dict(arrowstyle='->'))`
4. `plt.annotate('Point', xy=(2, 10), xytext=(3, 12), xycoords='data')`
5. `plt.annotate('A', xy=(1, 5)); plt.annotate('B', xy=(2, 10))`

#### text Questions
1. How do you add text at a specific coordinate on a plot?
2. How can you set a custom font size for text?
3. How do you change the color of text on a plot?
4. How can you rotate text on a plot?
5. How do you add text with a background color?

#### text Answers
1. `plt.text(2, 10, 'Text')`
2. `plt.text(2, 10, 'Text', fontsize=12)`
3. `plt.text(2, 10, 'Text', color='blue')`
4. `plt.text(2, 10, 'Text', rotation=45)`
5. `plt.text(2, 10, 'Text', bbox=dict(facecolor='yellow', alpha=0.5))`

---

### grid, twinx, colorbar

#### grid Questions
1. How do you add a grid to a plot?
2. How can you set a custom color for the grid lines?
3. How do you make the grid lines dashed?
4. How can you control the visibility of the grid?
5. How do you set the grid on a specific axis?

#### grid Answers
1. `plt.grid()`
2. `plt.grid(color='gray')`
3. `plt.grid(linestyle='--')`
4. `plt.grid(visible=True)`
5. `plt.grid(axis='y')`

#### twinx Questions
1. How do you create a second y-axis on the right side?
2. How can you plot different data on the twinx axis?
3. How do you set a label for the twinx axis?
4. How can you adjust the color of the twinx axis?
5. How do you share the x-axis with twinx?

#### twinx Answers
1. `ax2 = plt.twinx()`
2. `ax2.plot(x, y2, color='red')`
3. `ax2.set_ylabel('Y2 Axis')`
4. `ax2.tick_params(axis='y', colors='red')`
5. `ax2 = plt.twinx(); ax2.plot(x, y2)`

#### colorbar Questions
1. How do you add a colorbar to a scatter plot?
2. How can you set a custom label for a colorbar?
3. How do you adjust the size of a colorbar?
4. How can you change the colorbar orientation?
5. How do you add a colorbar with a specific range?

#### colorbar Answers
1. `plt.scatter(x, y, c=values); plt.colorbar()`
2. `plt.scatter(x, y, c=values); plt.colorbar(label='Values')`
3. `plt.scatter(x, y, c=values); plt.colorbar(shrink=0.5)`
4. `plt.scatter(x, y, c=values); plt.colorbar(orientation='horizontal')`
5. `plt.scatter(x, y, c=values); plt.colorbar(vmin=0, vmax=100)`

---

### savefig, tight_layout, loglog

#### savefig Questions
1. How do you save a plot to a PNG file?
2. How can you set a specific DPI when saving a figure?
3. How do you save a plot with a transparent background?
4. How can you specify the file format when saving?
5. How do you add a bounding box when saving a figure?

#### savefig Answers
1. `plt.savefig('plot.png')`
2. `plt.savefig('plot.png', dpi=300)`
3. `plt.savefig('plot.png', transparent=True)`
4. `plt.savefig('plot.svg')`
5. `plt.savefig('plot.png', bbox_inches='tight')`

#### tight_layout Questions
1. How do you automatically adjust subplot spacing?
2. How can you set a custom padding with tight_layout?
3. How do you apply tight_layout to a specific figure?
4. How can you adjust the height padding with tight_layout?
5. How do you use tight_layout with multiple subplots?

#### tight_layout Answers
1. `plt.tight_layout()`
2. `plt.tight_layout(pad=2.0)`
3. `fig = plt.figure(); fig.tight_layout()`
4. `plt.tight_layout(h_pad=1.5)`
5. `plt.subplot(2, 1, 1); plt.subplot(2, 1, 2); plt.tight_layout()`

#### loglog Questions
1. How do you create a log-log plot with x and y data?
2. How can you set a base for the log scale?
3. How do you add a grid to a log-log plot?
4. How can you adjust the limits on a log-log plot?
5. How do you label axes on a log-log plot?

#### loglog Answers
1. `plt.loglog(x, y)`
2. `plt.loglog(x, y, basex=10, basey=10)`
3. `plt.loglog(x, y); plt.grid(True)`
4. `plt.loglog(x, y); plt.ylim(1, 1000)`
5. `plt.loglog(x, y); plt.xlabel('X'); plt.ylabel('Y')`

---


## cheat sheet 
# Matplotlib Cheatsheet

## Basic Plotting Functions
### plot
- Create a line plot: `plt.plot(x, y)`
  - *Output*: A simple line connecting points defined by `x` and `y` coordinates.
- Customize color and linestyle: `plt.plot(x, y, color='red', linestyle='--')`
  - *Output*: A red dashed line connecting the points.
- Plot multiple lines: `plt.plot(x1, y1); plt.plot(x2, y2)`
  - *Output*: Two overlapping lines based on `x1, y1` and `x2, y2` coordinates.
- Add markers: `plt.plot(x, y, marker='o')`
  - *Output*: A line with circular markers at each data point.
- Set label for legend: `plt.plot(x, y, label='Data')`
  - *Output*: A line with a label "Data" that can be used in a legend (legend not shown until `plt.legend()` is called).

### scatter
- Create a scatter plot: `plt.scatter(x, y)`
  - *Output*: A scatter plot with points at each `x`, `y` coordinate pair.
- Vary point size: `plt.scatter(x, y, s=size)`
  - *Output*: Points with sizes proportional to the `size` array values.
- Use colormap for colors: `plt.scatter(x, y, c=values, cmap='viridis')`
  - *Output*: Points colored according to `values` using the 'viridis' colormap, with a colorbar if added.
- Adjust transparency: `plt.scatter(x, y, alpha=0.5)`
  - *Output*: Points with 50% transparency, allowing underlying points to show through.
- Add title: `plt.scatter(x, y); plt.title('Scatter Plot')`
  - *Output*: A scatter plot with the title "Scatter Plot" at the top.

### bar
- Create a bar plot: `plt.bar(x, height)`
  - *Output*: Vertical bars with `x` as categories and `height` as bar heights.
- Set different colors: `plt.bar(x, height, color=['red', 'blue', 'green'])`
  - *Output*: Bars colored red, blue, and green respectively for each `x` value.
- Create grouped bar plot: `plt.bar(x - 0.2, height1, width=0.4); plt.bar(x + 0.2, height2, width=0.4)`
  - *Output*: Two groups of bars side by side for each `x`, offset by 0.2.
- Add error bars: `plt.bar(x, height, yerr=error)`
  - *Output*: Bars with error bars indicating variability from the `error` array.
- Rotate x-axis labels: `plt.bar(x, height); plt.xticks(rotation=45)`
  - *Output*: Bars with x-axis labels rotated 45 degrees for better readability.

## Figure and Subplot Management
### subplot
- Create 2x2 grid: `plt.subplot(2, 2, 1)`
  - *Output*: A 2x2 grid of subplots, with the first subplot active.
- Plot in first subplot: `plt.subplot(1, 2, 1); plt.plot(x, y)`
  - *Output*: A line plot in the first of two subplots side by side.
- Adjust spacing: `plt.tight_layout()`
  - *Output*: Automatically adjusts subplot spacing to prevent overlap.
- Set subplot title: `plt.subplot(1, 2, 1); plt.plot(x, y); plt.title('Plot 1')`
  - *Output*: A line plot in the first subplot with the title "Plot 1".
- Share x-axis: `plt.subplot(2, 1, 1, sharex=plt.subplot(2, 1, 2)); plt.plot(x, y)`
  - *Output*: Two subplots stacked vertically sharing the x-axis.

### figure
- Create new figure: `plt.figure(figsize=(10, 6))`
  - *Output*: A new figure window with width 10 inches and height 6 inches.
- Set background color: `plt.figure(facecolor='lightgray')`
  - *Output*: A figure with a light gray background.
- Add figure title: `plt.figure(); plt.suptitle('Main Title')`
  - *Output*: A figure with a centered title "Main Title" above all subplots.
- Create multiple figures: `plt.figure(1); plt.plot(x1, y1); plt.figure(2); plt.plot(x2, y2)`
  - *Output*: Two separate figure windows with different line plots.
- Adjust DPI: `plt.figure(dpi=100)`
  - *Output*: A figure with 100 dots per inch resolution.

## Labels and Legends
### title
- Add title: `plt.title('My Plot')`
  - *Output*: Title "My Plot" displayed at the top of the plot.
- Set font size: `plt.title('My Plot', fontsize=14)`
  - *Output*: Title "My Plot" with a font size of 14.
- Center title: `plt.title('My Plot', loc='center')`
  - *Output*: Title "My Plot" centered horizontally.
- Set color: `plt.title('My Plot', color='blue')`
  - *Output*: Title "My Plot" in blue text.
- Adjust position: `plt.title('My Plot', pad=20)`
  - *Output*: Title "My Plot" moved 20 points away from the plot.

### xlabel
- Label x-axis: `plt.xlabel('X Axis')`
  - *Output*: "X Axis" label below the x-axis.
- Set font size: `plt.xlabel('X Axis', fontsize=12)`
  - *Output*: "X Axis" label with font size 12.
- Rotate label: `plt.xlabel('X Axis', rotation=45)`
  - *Output*: "X Axis" label rotated 45 degrees.
- Set color: `plt.xlabel('X Axis', color='green')`
  - *Output*: "X Axis" label in green text.
- Adjust position: `plt.xlabel('X Axis', labelpad=10)`
  - *Output*: "X Axis" label moved 10 points from the axis.

### ylabel
- Label y-axis: `plt.ylabel('Y Axis')`
  - *Output*: "Y Axis" label to the left of the y-axis.
- Set font size: `plt.ylabel('Y Axis', fontsize=12)`
  - *Output*: "Y Axis" label with font size 12.
- Rotate label: `plt.ylabel('Y Axis', rotation=0)`
  - *Output*: "Y Axis" label horizontal (0 degrees rotation).
- Set color: `plt.ylabel('Y Axis', color='red')`
  - *Output*: "Y Axis" label in red text.
- Adjust position: `plt.ylabel('Y Axis', labelpad=10)`
  - *Output*: "Y Axis" label moved 10 points from the axis.

### legend
- Add legend: `plt.plot(x, y, label='Line'); plt.legend()`
  - *Output*: A legend box with "Line" label for the plotted line.
- Set location: `plt.legend(loc='upper right')`
  - *Output*: Legend positioned in the upper right corner.
- Adjust font size: `plt.legend(fontsize=12)`
  - *Output*: Legend text with font size 12.
- Add title: `plt.legend(title='Legend Title')`
  - *Output*: Legend with a title "Legend Title".
- Make box transparent: `plt.legend(framealpha=0.5)`
  - *Output*: Legend box with 50% transparency.

## Annotations
### annotate
- Add annotation with arrow: `plt.annotate('Point', xy=(2, 10), xytext=(3, 15), arrowprops=dict(facecolor='black'))`
  - *Output*: Text "Point" at (3, 15) with an arrow pointing to (2, 10).
- Set color: `plt.annotate('Point', xy=(2, 10), xytext=(3, 15), color='red')`
  - *Output*: Text "Point" in red with an arrow.
- Adjust arrow style: `plt.annotate('Point', xy=(2, 10), xytext=(3, 15), arrowprops=dict(arrowstyle='->'))`
  - *Output*: Text "Point" with a right arrow style.
- Specify coordinates: `plt.annotate('Point', xy=(2, 10), xytext=(3, 12), xycoords='data')`
  - *Output*: Text "Point" at data coordinates (3, 12) with an arrow.
- Add multiple annotations: `plt.annotate('A', xy=(1, 5)); plt.annotate('B', xy=(2, 10))`
  - *Output*: Two text labels "A" and "B" at specified coordinates.

### text
- Add text: `plt.text(2, 10, 'Text')`
  - *Output*: Text "Text" displayed at coordinates (2, 10).
- Set font size: `plt.text(2, 10, 'Text', fontsize=12)`
  - *Output*: Text "Text" with font size 12.
- Change color: `plt.text(2, 10, 'Text', color='blue')`
  - *Output*: Text "Text" in blue.
- Rotate text: `plt.text(2, 10, 'Text', rotation=45)`
  - *Output*: Text "Text" rotated 45 degrees.
- Add background: `plt.text(2, 10, 'Text', bbox=dict(facecolor='yellow', alpha=0.5))`
  - *Output*: Text "Text" with a semi-transparent yellow background.

## Grid and Axes
### grid
- Add grid: `plt.grid()`
  - *Output*: Grid lines added to both axes.
- Set color: `plt.grid(color='gray')`
  - *Output*: Grid lines in gray color.
- Make dashed: `plt.grid(linestyle='--')`
  - *Output*: Grid lines as dashed lines.
- Control visibility: `plt.grid(visible=True)`
  - *Output*: Grid lines turned on (default behavior).
- Set axis: `plt.grid(axis='y')`
  - *Output*: Grid lines only on the y-axis.

### twinx
- Create second y-axis: `ax2 = plt.twinx()`
  - *Output*: A second y-axis on the right side of the plot.
- Plot on twinx: `ax2.plot(x, y2, color='red')`
  - *Output*: A red line on the right y-axis.
- Set label: `ax2.set_ylabel('Y2 Axis')`
  - *Output*: "Y2 Axis" label on the right y-axis.
- Adjust color: `ax2.tick_params(axis='y', colors='red')`
  - *Output*: Right y-axis ticks in red.
- Share x-axis: `ax2 = plt.twinx(); ax2.plot(x, y2)`
  - *Output*: Right y-axis with a plot sharing the x-axis.

### colorbar
- Add colorbar: `plt.scatter(x, y, c=values); plt.colorbar()`
  - *Output*: A colorbar alongside the scatter plot mapping colors to values.
- Set label: `plt.scatter(x, y, c=values); plt.colorbar(label='Values')`
  - *Output*: Colorbar with "Values" as the label.
- Adjust size: `plt.scatter(x, y, c=values); plt.colorbar(shrink=0.5)`
  - *Output*: A smaller colorbar (50% of default size).
- Change orientation: `plt.scatter(x, y, c=values); plt.colorbar(orientation='horizontal')`
  - *Output*: A horizontal colorbar below the plot.
- Set range: `plt.scatter(x, y, c=values); plt.colorbar(vmin=0, vmax=100)`
  - *Output*: Colorbar with a range from 0 to 100.

## Saving and Layout
### savefig
- Save to PNG: `plt.savefig('plot.png')`
  - *Output*: Saves the current figure as 'plot.png' in the working directory.
- Set DPI: `plt.savefig('plot.png', dpi=300)`
  - *Output*: Saves with 300 dots per inch resolution.
- Transparent background: `plt.savefig('plot.png', transparent=True)`
  - *Output*: Saves with a transparent background.
- Specify format: `plt.savefig('plot.svg')`
  - *Output*: Saves as an SVG file.
- Add bounding box: `plt.savefig('plot.png', bbox_inches='tight')`
  - *Output*: Saves with tight bounding box to include all elements.

### tight_layout
- Adjust spacing: `plt.tight_layout()`
  - *Output*: Automatically adjusts subplot spacing to prevent overlap.
- Set padding: `plt.tight_layout(pad=2.0)`
  - *Output*: Adjusts spacing with 2.0 padding in inches.
- Apply to figure: `fig = plt.figure(); fig.tight_layout()`
  - *Output*: Applies tight layout to the specified figure.
- Adjust height padding: `plt.tight_layout(h_pad=1.5)`
  - *Output*: Adjusts vertical padding between subplots.
- Use with subplots: `plt.subplot(2, 1, 1); plt.subplot(2, 1, 2); plt.tight_layout()`
  - *Output*: Adjusts spacing for a 2x1 subplot grid.

### loglog
- Create log-log plot: `plt.loglog(x, y)`
  - *Output*: A plot with both x and y axes on a logarithmic scale.
- Set base: `plt.loglog(x, y, basex=10, basey=10)`
  - *Output*: Log-log plot with base 10 for both axes.
- Add grid: `plt.loglog(x, y); plt.grid(True)`
  - *Output*: Log-log plot with a grid.
- Adjust limits: `plt.loglog(x, y); plt.ylim(1, 1000)`
  - *Output*: Log-log plot with y-axis limited from 1 to 1000.
- Label axes: `plt.loglog(x, y); plt.xlabel('X'); plt.ylabel('Y')`
  - *Output*: Log-log plot with "X" and "Y" axis labels.