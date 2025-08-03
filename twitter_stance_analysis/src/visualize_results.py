import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path

def load_analysis_results():
    """Load the analysis results from JSON file."""
    with open('results/detailed_analysis.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def create_stance_radar_chart(results):
    """Create a radar chart showing stance components for each user."""
    # Create figure
    plt.figure(figsize=(12, 8))
    
    # Get component names
    components = ['keyword_ratio', 'sentiment', 'hashtag_usage', 
                 'engagement', 'mention_patterns', 'content_length']
    
    # Number of variables
    N = len(components)
    
    # Compute angle for each axis
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Close the loop
    
    # Create subplot
    ax = plt.subplot(111, polar=True)
    
    # Set labels
    plt.xticks(angles[:-1], components)
    
    # Draw y-axis labels
    ax.set_rlabel_position(0)
    plt.yticks([0.25, 0.5, 0.75], ["0.25", "0.5", "0.75"], color="grey", size=8)
    plt.ylim(0, 1)
    
    # Plot data for each user
    colors = ['blue', 'green', 'red', 'purple']
    for i, (username, data) in enumerate(results.items()):
        # Get average component scores
        scores = []
        for component in components:
            avg_score = np.mean([post['component_scores'][component] 
                               for post in data['user_analysis']['tweet_analyses']])
            scores.append(avg_score)
        scores += scores[:1]  # Close the loop
        
        # Plot data
        ax.plot(angles, scores, linewidth=2, linestyle='solid', label=username.split('.')[0], color=colors[i])
        ax.fill(angles, scores, alpha=0.1, color=colors[i])
    
    # Add legend
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    plt.title('Stance Component Analysis by User', size=15)
    
    # Save plot
    plt.savefig('results/plots/stance_radar.png', bbox_inches='tight', dpi=300)
    plt.close()

def create_stance_heatmap(results):
    """Create a heatmap showing stance scores over time."""
    # Prepare data
    all_scores = []
    usernames = []
    
    for username, data in results.items():
        scores = [post['score'] for post in data['post_analyses']]
        all_scores.append(scores)
        usernames.append(username.split('.')[0])
    
    # Create DataFrame
    max_length = max(len(scores) for scores in all_scores)
    padded_scores = [scores + [np.nan] * (max_length - len(scores)) for scores in all_scores]
    df = pd.DataFrame(padded_scores, index=usernames)
    
    # Create heatmap
    plt.figure(figsize=(15, 8))
    sns.heatmap(df, cmap='RdBu_r', center=0, annot=False, 
                cbar_kws={'label': 'Stance Score'})
    plt.title('Stance Evolution Over Posts')
    plt.xlabel('Post Sequence')
    plt.ylabel('Users')
    
    # Save plot
    plt.savefig('results/plots/stance_heatmap.png', bbox_inches='tight', dpi=300)
    plt.close()

def create_stance_distribution(results):
    """Create a stacked bar chart showing stance distribution."""
    # Prepare data
    users = []
    pro_israeli = []
    pro_palestinian = []
    neutral = []
    
    for username, data in results.items():
        users.append(username.split('.')[0])
        stance_dist = data['user_analysis']['stance_distribution']
        pro_israeli.append(stance_dist.get('pro-Israeli', 0))
        pro_palestinian.append(stance_dist.get('pro-Palestinian', 0))
        neutral.append(stance_dist.get('neutral/unclear', 0))
    
    # Create DataFrame
    df = pd.DataFrame({
        'User': users,
        'Pro-Israeli': pro_israeli,
        'Pro-Palestinian': pro_palestinian,
        'Neutral': neutral
    })
    
    # Create stacked bar chart
    plt.figure(figsize=(12, 6))
    df.set_index('User').plot(kind='bar', stacked=True, 
                             color=['blue', 'green', 'gray'])
    plt.title('Stance Distribution by User')
    plt.xlabel('Users')
    plt.ylabel('Number of Posts')
    plt.xticks(rotation=45)
    plt.legend(title='Stance')
    plt.tight_layout()
    
    # Save plot
    plt.savefig('results/plots/stance_distribution.png', bbox_inches='tight', dpi=300)
    plt.close()

def create_confidence_plot(results):
    """Create a scatter plot of stance scores vs confidence."""
    # Prepare data
    scores = []
    confidences = []
    stances = []
    usernames = []
    
    for username, data in results.items():
        scores.append(data['user_analysis']['average_score'])
        confidences.append(data['user_analysis']['confidence'])
        stances.append(data['user_analysis']['stance'])
        usernames.append(username.split('.')[0])
    
    # Create scatter plot
    plt.figure(figsize=(12, 8))
    colors = {'pro-Israeli': 'blue', 'pro-Palestinian': 'green', 'neutral/unclear': 'gray'}
    
    for stance in colors:
        mask = [s == stance for s in stances]
        plt.scatter([s for s, m in zip(scores, mask) if m],
                   [c for c, m in zip(confidences, mask) if m],
                   c=colors[stance], label=stance, s=100, alpha=0.6)
    
    # Add user labels
    for username, score, conf in zip(usernames, scores, confidences):
        plt.annotate(username, (score, conf), xytext=(5, 5), 
                    textcoords='offset points')
    
    # Add reference lines
    plt.axvline(x=0, color='black', linestyle='--', alpha=0.3)
    plt.axhline(y=0.5, color='black', linestyle='--', alpha=0.3)
    
    # Customize plot
    plt.grid(True, alpha=0.3)
    plt.xlabel('Stance Score (negative = pro-Palestinian, positive = pro-Israeli)')
    plt.ylabel('Confidence Score')
    plt.title('User Stance Analysis')
    plt.legend()
    
    # Save plot
    plt.savefig('results/plots/stance_confidence.png', bbox_inches='tight', dpi=300)
    plt.close()

def visualize_stance_analysis(username=None):
    """Visualize stance analysis results from the JSON file."""
    # Load the analysis results
    results_file = Path('data/stance_analysis.json')
    if not results_file.exists():
        print("No analysis results found. Please run analyze_user.py first.")
        return
    
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # If username is provided, only show that user's results
    if username:
        if username not in results:
            print(f"No results found for user {username}")
            return
        results = {username: results[username]}
    
    # Create a figure with subplots for each user
    num_users = len(results)
    fig, axes = plt.subplots(num_users, 2, figsize=(15, 5 * num_users))
    if num_users == 1:
        axes = np.array([axes])
    
    for idx, (user, analysis) in enumerate(results.items()):
        # Plot 1: Stance Distribution Pie Chart
        stance_dist = analysis['stance_distribution']
        labels = list(stance_dist.keys())
        sizes = list(stance_dist.values())
        colors = ['#ff9999', '#66b3ff', '#99ff99']
        
        axes[idx, 0].pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                        startangle=90)
        axes[idx, 0].set_title(f'Stance Distribution for {user}')
        
        # Plot 2: Confidence and Score Bar Chart
        metrics = ['Confidence', 'Average Score']
        values = [analysis['confidence'], analysis['average_score']]
        colors = ['#ff9999', '#66b3ff']
        
        bars = axes[idx, 1].bar(metrics, values, color=colors)
        axes[idx, 1].set_ylim(0, 1)
        axes[idx, 1].set_title(f'Analysis Metrics for {user}')
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            axes[idx, 1].text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.2f}',
                            ha='center', va='bottom')
    
    plt.tight_layout()
    
    # Save the plot
    output_dir = Path('data/visualizations')
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f'stance_analysis_{username if username else "all"}.png'
    plt.savefig(output_file)
    print(f"Visualization saved to {output_file}")
    
    # Show the plot
    plt.show()

def main():
    # Create plots directory if it doesn't exist
    Path('results/plots').mkdir(parents=True, exist_ok=True)
    
    # Load results
    results = load_analysis_results()
    
    # Create visualizations
    print("Creating stance radar chart...")
    create_stance_radar_chart(results)
    
    print("Creating stance heatmap...")
    create_stance_heatmap(results)
    
    print("Creating stance distribution plot...")
    create_stance_distribution(results)
    
    print("Creating confidence plot...")
    create_confidence_plot(results)
    
    print("\nVisualizations have been saved to results/plots/")
    print("1. stance_radar.png - Shows how different components contribute to each user's stance")
    print("2. stance_heatmap.png - Shows how stance evolves over posts")
    print("3. stance_distribution.png - Shows the distribution of stances for each user")
    print("4. stance_confidence.png - Shows stance scores vs confidence levels")

    import sys
    if len(sys.argv) > 1:
        username = sys.argv[1]
        visualize_stance_analysis(username)
    else:
        visualize_stance_analysis()

if __name__ == "__main__":
    main() 