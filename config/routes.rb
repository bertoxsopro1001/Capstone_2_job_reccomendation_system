# config/routes.rb

Rails.application.routes.draw do
  get '/jobs', to: 'jobs#index'
  post '/recommend_jobs', to: 'jobs#recommend_jobs'
  get '/recommended_jobs', to: 'jobs#recommended_jobs', as: 'recommended_jobs'
end
