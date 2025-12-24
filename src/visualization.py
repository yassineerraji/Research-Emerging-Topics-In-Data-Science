"""
Visualization Module

Handles plotting and visualization for climate scenario analysis.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import List, Optional, Dict
from . import config

# Set visualization style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


def plot_time_series(data: pd.DataFrame,
                    datetime_col: str,
                    value_cols: List[str],
                    title: str = "Time Series",
                    save_path: Optional[str] = None):
    """
    Plot time series data.
    
    Args:
        data (pd.DataFrame): Input data
        datetime_col (str): Datetime column
        value_cols (list): Variables to plot
        title (str): Plot title
        save_path (str): Path to save figure
    """
    fig, ax = plt.subplots(figsize=(14, 6))
    
    for col in value_cols:
        ax.plot(data[datetime_col], data[col], label=col, linewidth=2)
    
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Value', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=config.VIZ_CONFIG['dpi'], bbox_inches='tight')
        print(f"Time series plot saved to: {save_path}")
    
    plt.show()


def plot_scenario_comparison(data: pd.DataFrame,
                            datetime_col: str,
                            value_col: str,
                            scenario_col: str,
                            scenarios: Optional[List[str]] = None,
                            title: str = "Scenario Comparison",
                            save_path: Optional[str] = None):
    """
    Plot comparison of multiple scenarios.
    
    Args:
        data (pd.DataFrame): Input data
        datetime_col (str): Datetime column
        value_col (str): Variable to plot
        scenario_col (str): Scenario identifier column
        scenarios (list): Specific scenarios to plot (None = all)
        title (str): Plot title
        save_path (str): Path to save figure
    """
    fig, ax = plt.subplots(figsize=(14, 7))
    
    if scenarios is None:
        scenarios = data[scenario_col].unique()
    
    colors = plt.cm.viridis(np.linspace(0, 1, len(scenarios)))
    
    for scenario, color in zip(scenarios, colors):
        scenario_data = data[data[scenario_col] == scenario]
        ax.plot(scenario_data[datetime_col], scenario_data[value_col],
               label=scenario, linewidth=2.5, color=color)
    
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel(value_col.replace('_', ' ').title(), fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(fontsize=10, loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=config.VIZ_CONFIG['dpi'], bbox_inches='tight')
        print(f"Scenario comparison plot saved to: {save_path}")
    
    plt.show()


def plot_anomaly_heatmap(data: pd.DataFrame,
                        datetime_col: str,
                        region_col: str,
                        value_col: str,
                        title: str = "Anomaly Heatmap",
                        save_path: Optional[str] = None):
    """
    Plot heatmap of anomalies across regions and time.
    
    Args:
        data (pd.DataFrame): Input data
        datetime_col (str): Datetime column
        region_col (str): Region/location column
        value_col (str): Value column (should be anomaly)
        title (str): Plot title
        save_path (str): Path to save figure
    """
    # Pivot data for heatmap
    pivot_data = data.pivot_table(
        values=value_col,
        index=region_col,
        columns=datetime_col,
        aggfunc='mean'
    )
    
    fig, ax = plt.subplots(figsize=(16, 8))
    
    sns.heatmap(pivot_data, cmap='RdBu_r', center=0, ax=ax,
               cbar_kws={'label': value_col.replace('_', ' ').title()})
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Region', fontsize=12)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=config.VIZ_CONFIG['dpi'], bbox_inches='tight')
        print(f"Heatmap saved to: {save_path}")
    
    plt.show()


def plot_distribution_comparison(data: pd.DataFrame,
                                value_col: str,
                                group_col: str,
                                title: str = "Distribution Comparison",
                                save_path: Optional[str] = None):
    """
    Plot distribution comparison across groups.
    
    Args:
        data (pd.DataFrame): Input data
        value_col (str): Value column to plot
        group_col (str): Grouping variable (e.g., scenario)
        title (str): Plot title
        save_path (str): Path to save figure
    """
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Violin plot
    sns.violinplot(data=data, x=group_col, y=value_col, ax=axes[0])
    axes[0].set_title('Violin Plot', fontsize=12, fontweight='bold')
    axes[0].set_xlabel(group_col.replace('_', ' ').title(), fontsize=10)
    axes[0].set_ylabel(value_col.replace('_', ' ').title(), fontsize=10)
    axes[0].tick_params(axis='x', rotation=45)
    
    # Box plot
    sns.boxplot(data=data, x=group_col, y=value_col, ax=axes[1])
    axes[1].set_title('Box Plot', fontsize=12, fontweight='bold')
    axes[1].set_xlabel(group_col.replace('_', ' ').title(), fontsize=10)
    axes[1].set_ylabel(value_col.replace('_', ' ').title(), fontsize=10)
    axes[1].tick_params(axis='x', rotation=45)
    
    fig.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=config.VIZ_CONFIG['dpi'], bbox_inches='tight')
        print(f"Distribution plot saved to: {save_path}")
    
    plt.show()


def plot_projection_uncertainty(projections: Dict[str, pd.DataFrame],
                               datetime_col: str,
                               value_col: str,
                               title: str = "Projection Uncertainty",
                               save_path: Optional[str] = None):
    """
    Plot projections with uncertainty bands.
    
    Args:
        projections (dict): Dictionary of {scenario: projection_df}
        datetime_col (str): Datetime column
        value_col (str): Value column
        title (str): Plot title
        save_path (str): Path to save figure
    """
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Combine all projections
    all_projections = []
    for scenario, proj_df in projections.items():
        proj_df = proj_df.copy()
        proj_df['scenario'] = scenario
        all_projections.append(proj_df)
    
    combined = pd.concat(all_projections, ignore_index=True)
    
    # Compute statistics by time
    stats = combined.groupby(datetime_col)[value_col].agg(['mean', 'std', 'min', 'max'])
    
    # Plot mean line
    ax.plot(stats.index, stats['mean'], color='darkblue', linewidth=3, label='Mean')
    
    # Plot uncertainty band (±1 std)
    ax.fill_between(stats.index,
                    stats['mean'] - stats['std'],
                    stats['mean'] + stats['std'],
                    alpha=0.3, color='blue', label='±1 Std Dev')
    
    # Plot min-max range
    ax.fill_between(stats.index,
                    stats['min'],
                    stats['max'],
                    alpha=0.15, color='lightblue', label='Min-Max Range')
    
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel(value_col.replace('_', ' ').title(), fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(fontsize=10, loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=config.VIZ_CONFIG['dpi'], bbox_inches='tight')
        print(f"Uncertainty plot saved to: {save_path}")
    
    plt.show()


def plot_scenario_summary_table(summary_df: pd.DataFrame,
                               save_path: Optional[str] = None):
    """
    Create a visual table summary of scenario statistics.
    
    Args:
        summary_df (pd.DataFrame): Summary statistics dataframe
        save_path (str): Path to save figure
    """
    fig, ax = plt.subplots(figsize=(12, len(summary_df) * 0.5 + 1))
    ax.axis('tight')
    ax.axis('off')
    
    # Format numbers
    formatted_df = summary_df.copy()
    for col in formatted_df.select_dtypes(include=[np.number]).columns:
        formatted_df[col] = formatted_df[col].round(2)
    
    table = ax.table(cellText=formatted_df.values,
                    colLabels=formatted_df.columns,
                    cellLoc='center',
                    loc='center',
                    bbox=[0, 0, 1, 1])
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    
    # Style header
    for i in range(len(formatted_df.columns)):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Alternate row colors
    for i in range(1, len(formatted_df) + 1):
        for j in range(len(formatted_df.columns)):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#f1f1f2')
    
    plt.title('Scenario Summary Statistics', fontsize=14, fontweight='bold', pad=20)
    
    if save_path:
        plt.savefig(save_path, dpi=config.VIZ_CONFIG['dpi'], bbox_inches='tight')
        print(f"Summary table saved to: {save_path}")
    
    plt.show()


def create_dashboard(data: pd.DataFrame,
                    datetime_col: str,
                    value_cols: List[str],
                    scenario_col: Optional[str] = None,
                    save_path: Optional[str] = None):
    """
    Create a comprehensive dashboard with multiple plots.
    
    Args:
        data (pd.DataFrame): Input data
        datetime_col (str): Datetime column
        value_cols (list): Variables to visualize
        scenario_col (str): Scenario column (optional)
        save_path (str): Path to save figure
    """
    n_plots = len(value_cols)
    n_rows = (n_plots + 1) // 2
    
    fig, axes = plt.subplots(n_rows, 2, figsize=(16, 5*n_rows))
    axes = axes.flatten() if n_plots > 1 else [axes]
    
    for idx, col in enumerate(value_cols):
        if scenario_col and scenario_col in data.columns:
            for scenario in data[scenario_col].unique():
                scenario_data = data[data[scenario_col] == scenario]
                axes[idx].plot(scenario_data[datetime_col], scenario_data[col],
                             label=scenario, linewidth=2)
        else:
            axes[idx].plot(data[datetime_col], data[col], linewidth=2)
        
        axes[idx].set_title(col.replace('_', ' ').title(), fontsize=11, fontweight='bold')
        axes[idx].set_xlabel('Time', fontsize=9)
        axes[idx].set_ylabel('Value', fontsize=9)
        axes[idx].grid(True, alpha=0.3)
        if scenario_col:
            axes[idx].legend(fontsize=8)
    
    # Hide extra subplots
    for idx in range(len(value_cols), len(axes)):
        axes[idx].axis('off')
    
    fig.suptitle('Climate Scenario Dashboard', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=config.VIZ_CONFIG['dpi'], bbox_inches='tight')
        print(f"Dashboard saved to: {save_path}")
    
    plt.show()


if __name__ == "__main__":
    print("Visualization module loaded.")
    print("Available functions: plot_time_series, plot_scenario_comparison, etc.")
