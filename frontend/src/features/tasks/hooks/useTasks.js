import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { tasksApi } from "../api";

export function useProjectTasks(projectId) {
  return useQuery({
    queryKey: ["tasks", { project: projectId }],
    queryFn: () => tasksApi.list({ project: projectId, page_size: 100 }),
    enabled: !!projectId,
  });
}

export function useTask(id) {
  return useQuery({ queryKey: ["task", id], queryFn: () => tasksApi.get(id), enabled: !!id });
}

export function useTaskComments(id) {
  return useQuery({ queryKey: ["task", id, "comments"], queryFn: () => tasksApi.comments(id), enabled: !!id });
}

export function useTransitionTask(projectId) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, status }) => tasksApi.transition(id, status),
    onSettled: () => qc.invalidateQueries({ queryKey: ["tasks", { project: projectId }] }),
  });
}

export function useSetProgress(projectId) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, value }) => tasksApi.progress(id, value),
    onSettled: () => qc.invalidateQueries({ queryKey: ["tasks", { project: projectId }] }),
  });
}

export function useCreateTask(projectId) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: tasksApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["tasks", { project: projectId }] }),
  });
}

export function useAddComment(taskId) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body) => tasksApi.addComment(taskId, body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["task", taskId, "comments"] }),
  });
}
