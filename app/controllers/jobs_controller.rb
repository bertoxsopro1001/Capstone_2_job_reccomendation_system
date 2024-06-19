# app/controllers/jobs_controller.rb

require 'httparty'

class JobsController < ApplicationController
  def index
    # Render the form to collect user preferences
  end

  def recommend_jobs
    user_input = {
      personality: params[:personality],
      work_experience: params[:work_experience],
      work_hours: params[:work_hours],
      salary: params[:salary]  # Pass salary range as a string
    }

    # Make a POST request to the Flask API endpoint
    api_url = 'http://localhost:5000/recommend_jobs'
    response = HTTParty.post(api_url, body: user_input.to_json, headers: { 'Content-Type' => 'application/json' })

    if response.code == 200
      @recommended_jobs = JSON.parse(response.body)

      # Handle the case where @recommended_jobs is nil or empty
      @recommended_jobs = [] if @recommended_jobs.nil?

      # Sort @recommended_jobs by salary in descending order to get the top recommendations
      @recommended_jobs = @recommended_jobs.sort_by { |job| -job['salary'] }.first(3)

      # Redirect to recommended_jobs action with @recommended_jobs as parameter
      redirect_to recommended_jobs_path(recommended_jobs: @recommended_jobs)
    else
      flash[:alert] = 'Error fetching job recommendations.'
      redirect_to jobs_path  # Redirect to index page if there's an error
    end
  end

  def recommended_jobs
    @recommended_jobs = params[:recommended_jobs]
  end
end
