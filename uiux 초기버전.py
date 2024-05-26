import tkinter as tk
from tkinter import messagebox

# Sample data for book recommendations
book_recommendations = {
    "Fantasy": ["Harry Potter", "Lord of the Rings", "The Hobbit"],
    "Science Fiction": ["Dune", "Neuromancer", "Foundation"],
    "Mystery": ["Gone Girl", "The Girl with the Dragon Tattoo", "In the Woods"],
    "Non-Fiction": ["Sapiens", "Educated", "Becoming"]
}

def recommend_books():
    category = entry.get().strip()
    if category in book_recommendations:
        recommendations = book_recommendations[category]
        result_text = "\n".join(recommendations)
        result_label.config(text=result_text)
    else:
        messagebox.showinfo("Error", "Category not found. Please try again.")

# Create the main window
root = tk.Tk()
root.title("Book Recommendation System")

# Set window size
root.geometry("400x300")

# Create a label for instructions
instruction_label = tk.Label(root, text="Enter a book category:", font=("Helvetica", 14))
instruction_label.pack(pady=10)

# Create an entry widget for user input
entry = tk.Entry(root, width=50, font=("Helvetica", 12))
entry.pack(pady=10)

# Create a button to trigger the book recommendation
recommend_button = tk.Button(root, text="Recommend Books", command=recommend_books, font=("Helvetica", 12))
recommend_button.pack(pady=10)

# Create a label to display the recommended books
result_label = tk.Label(root, text="", justify=tk.LEFT, font=("Helvetica", 12))
result_label.pack(pady=20)

# Run the application
root.mainloop()