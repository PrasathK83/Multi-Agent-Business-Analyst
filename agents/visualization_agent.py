"""Visualization agent that returns Plotly specs for the frontend."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import seaborn as sns

from utils.config import CHART_TYPES, COLOR_PALETTE, MATPLOTLIB_STYLE, PLOTLY_TEMPLATE
from utils.session_manager import SessionManager


class VisualizationAgent:
    """Generate matplotlib + Plotly figures without Streamlit dependencies."""

    def __init__(self, session: SessionManager):
        self.session = session
        # Set matplotlib style
        try:
            plt.style.use(MATPLOTLIB_STYLE)
        except:
            plt.style.use('default')
        
        # Set seaborn defaults
        sns.set_palette(COLOR_PALETTE)
    
    def recommend_chart_type(self, df: pd.DataFrame, x_col: str = None, y_col: str = None) -> str:
        """
        Recommend best chart type based on data characteristics
        
        Args:
            df: pandas DataFrame
            x_col: X-axis column (optional)
            y_col: Y-axis column (optional)
            
        Returns:
            Recommended chart type
        """
        # If specific columns provided
        if x_col and y_col:
            x_dtype = df[x_col].dtype
            y_dtype = df[y_col].dtype
            
            # Both numeric -> scatter
            if pd.api.types.is_numeric_dtype(x_dtype) and pd.api.types.is_numeric_dtype(y_dtype):
                return 'scatter'
            
            # One categorical, one numeric -> bar
            if pd.api.types.is_numeric_dtype(y_dtype):
                return 'bar'
            
            return 'bar'
        
        # Auto-detect based on data
        numeric_cols = df.select_dtypes(include=['number']).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        # If we have categorical and numeric -> bar chart
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            return 'bar'
        
        # If only numeric -> histogram or line
        if len(numeric_cols) > 0:
            return 'histogram'
        
        # Default
        return 'bar'
    
    def create_bar_chart(self, df: pd.DataFrame, x_col: str, y_col: str, title: str = None) -> Tuple[Any, Any]:
        """
        Create bar chart using both Matplotlib and Plotly
        
        Args:
            df: pandas DataFrame
            x_col: X-axis column
            y_col: Y-axis column
            title: Chart title
            
        Returns:
            Tuple of (matplotlib_fig, plotly_fig)
        """
        if title is None:
            title = f"{y_col} by {x_col}"
        
        # Aggregate if needed
        if df[x_col].dtype == 'object':
            plot_data = df.groupby(x_col)[y_col].sum().reset_index()
        else:
            plot_data = df[[x_col, y_col]].copy()
        
        # Matplotlib version
        fig_mpl, ax = plt.subplots(figsize=(10, 6))
        ax.bar(plot_data[x_col].astype(str), plot_data[y_col], color=COLOR_PALETTE[0])
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(title)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Plotly version
        fig_plotly = px.bar(
            plot_data,
            x=x_col,
            y=y_col,
            title=title,
            template=PLOTLY_TEMPLATE,
            color_discrete_sequence=COLOR_PALETTE
        )
        fig_plotly.update_layout(
            xaxis_title=x_col,
            yaxis_title=y_col,
            hovermode='x unified'
        )
        
        return fig_mpl, fig_plotly
    
    def create_line_chart(self, df: pd.DataFrame, x_col: str, y_col: str, title: str = None) -> Tuple[Any, Any]:
        """Create line chart"""
        if title is None:
            title = f"{y_col} over {x_col}"
        
        # Matplotlib version
        fig_mpl, ax = plt.subplots(figsize=(10, 6))
        ax.plot(df[x_col], df[y_col], color=COLOR_PALETTE[0], linewidth=2, marker='o')
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Plotly version
        fig_plotly = px.line(
            df,
            x=x_col,
            y=y_col,
            title=title,
            template=PLOTLY_TEMPLATE,
            markers=True
        )
        fig_plotly.update_traces(line_color=COLOR_PALETTE[0])
        
        return fig_mpl, fig_plotly
    
    def create_pie_chart(self, df: pd.DataFrame, names_col: str, values_col: str = None, title: str = None) -> Tuple[Any, Any]:
        """Create pie chart"""
        if title is None:
            title = f"Distribution of {names_col}"
        
        # Prepare data
        if values_col:
            plot_data = df.groupby(names_col)[values_col].sum()
        else:
            plot_data = df[names_col].value_counts()
        
        # Limit to top 10 categories
        if len(plot_data) > 10:
            plot_data = plot_data.nlargest(10)
        
        # Matplotlib version
        fig_mpl, ax = plt.subplots(figsize=(10, 8))
        ax.pie(plot_data.values, labels=plot_data.index, autopct='%1.1f%%', colors=COLOR_PALETTE)
        ax.set_title(title)
        
        # Plotly version
        fig_plotly = px.pie(
            values=plot_data.values,
            names=plot_data.index,
            title=title,
            template=PLOTLY_TEMPLATE,
            color_discrete_sequence=COLOR_PALETTE
        )
        
        return fig_mpl, fig_plotly
    
    def create_histogram(self, df: pd.DataFrame, column: str, bins: int = 30, title: str = None) -> Tuple[Any, Any]:
        """Create histogram"""
        if title is None:
            title = f"Distribution of {column}"
        
        # Matplotlib version
        fig_mpl, ax = plt.subplots(figsize=(10, 6))
        ax.hist(df[column].dropna(), bins=bins, color=COLOR_PALETTE[0], edgecolor='black', alpha=0.7)
        ax.set_xlabel(column)
        ax.set_ylabel('Frequency')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Plotly version
        fig_plotly = px.histogram(
            df,
            x=column,
            nbins=bins,
            title=title,
            template=PLOTLY_TEMPLATE,
            color_discrete_sequence=COLOR_PALETTE
        )
        
        return fig_mpl, fig_plotly
    
    def create_scatter_plot(self, df: pd.DataFrame, x_col: str, y_col: str, title: str = None) -> Tuple[Any, Any]:
        """Create scatter plot"""
        if title is None:
            title = f"{y_col} vs {x_col}"
        
        # Matplotlib version
        fig_mpl, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(df[x_col], df[y_col], color=COLOR_PALETTE[0], alpha=0.6)
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Plotly version
        fig_plotly = px.scatter(
            df,
            x=x_col,
            y=y_col,
            title=title,
            template=PLOTLY_TEMPLATE,
            color_discrete_sequence=COLOR_PALETTE
        )
        
        return fig_mpl, fig_plotly
    
    def create_box_plot(self, df: pd.DataFrame, column: str, group_by: str = None, title: str = None) -> Tuple[Any, Any]:
        """Create box plot"""
        if title is None:
            title = f"Box Plot of {column}"
            if group_by:
                title += f" by {group_by}"
        
        # Matplotlib version
        fig_mpl, ax = plt.subplots(figsize=(10, 6))
        if group_by:
            df.boxplot(column=column, by=group_by, ax=ax)
        else:
            df.boxplot(column=column, ax=ax)
        ax.set_title(title)
        plt.tight_layout()
        
        # Plotly version
        if group_by:
            fig_plotly = px.box(
                df,
                x=group_by,
                y=column,
                title=title,
                template=PLOTLY_TEMPLATE,
                color_discrete_sequence=COLOR_PALETTE
            )
        else:
            fig_plotly = px.box(
                df,
                y=column,
                title=title,
                template=PLOTLY_TEMPLATE,
                color_discrete_sequence=COLOR_PALETTE
            )
        
        return fig_mpl, fig_plotly
    
    def create_heatmap(self, df: pd.DataFrame, title: str = "Correlation Heatmap") -> Tuple[Any, Any]:
        """Create correlation heatmap for numeric columns"""
        numeric_df = df.select_dtypes(include=['number'])
        
        if numeric_df.shape[1] < 2:
            return None, None
        
        corr_matrix = numeric_df.corr()
        
        # Matplotlib version
        fig_mpl, ax = plt.subplots(figsize=(12, 10))
        sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0, ax=ax)
        ax.set_title(title)
        plt.tight_layout()
        
        # Plotly version
        fig_plotly = px.imshow(
            corr_matrix,
            title=title,
            template=PLOTLY_TEMPLATE,
            color_continuous_scale='RdBu_r',
            aspect='auto'
        )
        
        return fig_mpl, fig_plotly
    
    def auto_visualize(self, df: pd.DataFrame, max_charts: int = 3) -> List[dict]:
        """
        Automatically generate relevant visualizations
        
        Args:
            df: pandas DataFrame
            max_charts: Maximum number of charts to generate
            
        Returns:
            List of chart dictionaries
        """
        charts = []
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Chart 1: If we have categorical and numeric -> bar chart
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]
            
            # Limit categories
            if df[cat_col].nunique() <= 20:
                fig_mpl, fig_plotly = self.create_bar_chart(df, cat_col, num_col)
                charts.append({
                    'type': 'bar',
                    'title': f"{num_col} by {cat_col}",
                    'matplotlib': fig_mpl,
                    'plotly': fig_plotly
                })
        
        # Chart 2: Distribution of first numeric column
        if len(numeric_cols) > 0 and len(charts) < max_charts:
            num_col = numeric_cols[0]
            fig_mpl, fig_plotly = self.create_histogram(df, num_col)
            charts.append({
                'type': 'histogram',
                'title': f"Distribution of {num_col}",
                'matplotlib': fig_mpl,
                'plotly': fig_plotly
            })
        
        # Chart 3: Correlation heatmap if multiple numeric columns
        if len(numeric_cols) >= 2 and len(charts) < max_charts:
            fig_mpl, fig_plotly = self.create_heatmap(df)
            if fig_mpl and fig_plotly:
                charts.append({
                    'type': 'heatmap',
                    'title': 'Correlation Heatmap',
                    'matplotlib': fig_mpl,
                    'plotly': fig_plotly
                })
        
        return charts

    def serialize_plotly(self, plotly_fig, title: str, chart_type: str) -> Dict[str, Any]:
        return {
            'title': title,
            'type': chart_type,
            'figure': plotly_fig.to_dict()
        }

    def execute(
        self,
        chart_type: Optional[str] = None,
        x_col: Optional[str] = None,
        y_col: Optional[str] = None,
        auto: bool = False
    ) -> Dict[str, Any]:
        df = self.session.get_dataframe('current')

        if df is None:
            return {'success': False, 'message': 'No data available. Upload data first.'}

        try:
            charts_payload: List[Dict[str, Any]] = []

            if auto:
                charts = self.auto_visualize(df)
                for chart_info in charts:
                    self.session.add_chart(
                        chart_info['matplotlib'],
                        chart_info['type'],
                        chart_info['title']
                    )
                    charts_payload.append(self.serialize_plotly(
                        chart_info['plotly'],
                        chart_info['title'],
                        chart_info['type']
                    ))

                return {
                    'success': True,
                    'charts': charts_payload,
                    'message': f"Generated {len(charts_payload)} visualizations"
                }

            if not chart_type or not x_col:
                return {'success': False, 'message': 'Chart type and X-axis column are required.'}

            if chart_type not in CHART_TYPES:
                return {'success': False, 'message': f'Unsupported chart type: {chart_type}'}

            if chart_type in ['bar', 'line', 'scatter'] and not y_col:
                return {'success': False, 'message': f'{chart_type.title()} chart requires both X and Y columns.'}

            if chart_type == 'bar':
                figs = self.create_bar_chart(df, x_col, y_col)
            elif chart_type == 'line':
                figs = self.create_line_chart(df, x_col, y_col)
            elif chart_type == 'pie':
                figs = self.create_pie_chart(df, x_col, y_col)
            elif chart_type == 'histogram':
                figs = self.create_histogram(df, x_col)
            elif chart_type == 'scatter':
                figs = self.create_scatter_plot(df, x_col, y_col)
            elif chart_type == 'box':
                figs = self.create_box_plot(df, x_col, y_col)
            elif chart_type == 'heatmap':
                figs = self.create_heatmap(df)
            else:
                return {'success': False, 'message': f'Unknown chart type: {chart_type}'}

            if not figs[0] or not figs[1]:
                return {'success': False, 'message': 'Unable to generate chart with selected options.'}

            title = f"Custom {chart_type} chart"
            self.session.add_chart(figs[0], chart_type, title)
            charts_payload.append(self.serialize_plotly(figs[1], title, chart_type))

            return {'success': True, 'charts': charts_payload, 'message': 'Chart generated successfully.'}

        except Exception as exc:
            return {'success': False, 'message': f'Error generating visualization: {exc}'}
