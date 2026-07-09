import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { projectsApi } from "../api";

export function useProjects(params) {
  return useQuery({ queryKey: ["projects", params], queryFn: () => projectsApi.list(params) });
}

export function useProject(id) {
  return useQuery({ queryKey: ["project", id], queryFn: () => projectsApi.get(id), enabled: !!id });
}

export function useCreateProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: projectsApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["projects"] }),
  });
}

export function useUpdateProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => projectsApi.update(id, data),
    onSuccess: (p) => {
      qc.invalidateQueries({ queryKey: ["projects"] });
      qc.invalidateQueries({ queryKey: ["project", p.id] });
    },
  });
}
