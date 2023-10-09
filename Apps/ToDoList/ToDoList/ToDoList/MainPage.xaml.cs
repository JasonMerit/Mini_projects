using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Xamarin.Forms;

namespace ToDoList
{
    public partial class MainPage : ContentPage
    {
        ObservableCollection<TaskItem> tasks = new ObservableCollection<TaskItem>();
        public MainPage()
        {
            InitializeComponent();
            tasks.Add(new TaskItem { Title = "Buy groceries", IsCompleted = false });
            taskListView.ItemsSource = tasks;
        }

        private void AddTaskButton_Clicked(object sender, EventArgs e)
        {
            string newTaskTitle = newTaskEntry.Text;
            if (!string.IsNullOrWhiteSpace(newTaskTitle))
            {
                tasks.Add(new TaskItem { Title = newTaskTitle, IsCompleted = false });
                newTaskEntry.Text = ""; // Clear the entry field after adding
            }
        }

    }

    public class TaskItem
    {
        public string Title { get; set; }
        public bool IsCompleted { get; set; }
    }


}
