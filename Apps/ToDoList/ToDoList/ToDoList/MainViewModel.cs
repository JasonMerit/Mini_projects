using System;
using System.Collections.ObjectModel;
using ToDoList;

namespace ToDoList
{
	public class MainViewModel
	{
		public ObservableCollection<TaskItem> Tasks { get; set; }

		public MainViewModel() 
		{ 
			Tasks = new ObservableCollection<TaskItem>();
		}

		public ICommand AddTaskCommand => new Command(AddTask);
	}
}

